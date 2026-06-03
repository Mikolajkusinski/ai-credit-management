using Microsoft.AspNetCore.Mvc;
using WebApi.Models;
using WebApi.Services;

namespace WebApi.Controllers;

[ApiController]
[Route("api/v1/monitoring")]
public class MonitoringController : ControllerBase
{
    private readonly MonitoringService _monitoringService;
    private readonly ILogger<MonitoringController> _logger;

    public MonitoringController(MonitoringService monitoringService, ILogger<MonitoringController> logger)
    {
        _monitoringService = monitoringService;
        _logger = logger;
    }

    /// <summary>
    /// Stateless sliding-window scoring: returns a 4-point PD trajectory (W0..W3) plus per-model
    /// trends for one client snapshot. Proxies the Flask <c>/predict/timeseries</c> engine and adds
    /// window labels. Does not persist anything (see monitoring API contract 4.2).
    /// </summary>
    [HttpPost("predict-timeseries")]
    [ProducesResponseType(typeof(TimeseriesResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorEnvelope), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ErrorEnvelope), StatusCodes.Status502BadGateway)]
    [ProducesResponseType(typeof(ErrorEnvelope), StatusCodes.Status503ServiceUnavailable)]
    public async Task<IActionResult> PredictTimeseries([FromBody] TimeseriesRequest request)
    {
        try
        {
            _logger.LogInformation("Received timeseries prediction request");
            var result = await _monitoringService.PredictTimeseriesAsync(request);

            if (result == null)
            {
                return StatusCode(StatusCodes.Status502BadGateway,
                    ErrorEnvelope.MlServiceError("ML service returned an empty response"));
            }

            return Ok(result);
        }
        catch (MlServiceException ex) when (ex.UpstreamStatusCode is not null)
        {
            _logger.LogError(ex, "ML service returned an error status");
            return StatusCode(StatusCodes.Status502BadGateway,
                ErrorEnvelope.MlServiceError(ex.Message));
        }
        catch (MlServiceException ex)
        {
            _logger.LogError(ex, "ML service unreachable");
            return StatusCode(StatusCodes.Status503ServiceUnavailable,
                ErrorEnvelope.MlServiceUnavailable(ex.Message));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing timeseries prediction request");
            return StatusCode(StatusCodes.Status500InternalServerError,
                ErrorEnvelope.Internal("An error occurred while processing your request"));
        }
    }

    /// <summary>
    /// Stateful scoring: scores a client snapshot, then persists the snapshot, its W3 predictions,
    /// and the per-model trends (monitoring API contract 4.3). Auto-creates the client when
    /// <c>{clientRef}</c> is new. Rejects a duplicate <c>(clientRef, snapshotDate)</c> with 409.
    /// </summary>
    [HttpPost("clients/{clientRef}/snapshots")]
    [ProducesResponseType(typeof(SnapshotResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ErrorEnvelope), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ErrorEnvelope), StatusCodes.Status409Conflict)]
    [ProducesResponseType(typeof(ErrorEnvelope), StatusCodes.Status502BadGateway)]
    [ProducesResponseType(typeof(ErrorEnvelope), StatusCodes.Status503ServiceUnavailable)]
    public async Task<IActionResult> CreateSnapshot(string clientRef, [FromBody] SnapshotRequest request)
    {
        if (string.IsNullOrWhiteSpace(clientRef) || clientRef.Length > 64)
        {
            return BadRequest(ErrorEnvelope.ValidationFailed(
                "clientRef must be between 1 and 64 characters", new { field = "clientRef" }));
        }

        if (request.SnapshotDate is { } date && date > DateOnly.FromDateTime(DateTime.UtcNow))
        {
            return BadRequest(ErrorEnvelope.ValidationFailed(
                "snapshotDate must not be in the future", new { field = "snapshotDate" }));
        }

        try
        {
            _logger.LogInformation("Received snapshot write request for client {ClientRef}", clientRef);
            var result = await _monitoringService.ScoreAndPersistAsync(clientRef, request);
            return StatusCode(StatusCodes.Status201Created, result);
        }
        catch (SnapshotConflictException ex)
        {
            _logger.LogWarning(ex, "Duplicate snapshot for client {ClientRef}", clientRef);
            return Conflict(ErrorEnvelope.Conflict(ex.Message));
        }
        catch (MlServiceException ex) when (ex.UpstreamStatusCode is not null)
        {
            _logger.LogError(ex, "ML service returned an error status");
            return StatusCode(StatusCodes.Status502BadGateway,
                ErrorEnvelope.MlServiceError(ex.Message));
        }
        catch (MlServiceException ex)
        {
            _logger.LogError(ex, "ML service unreachable");
            return StatusCode(StatusCodes.Status503ServiceUnavailable,
                ErrorEnvelope.MlServiceUnavailable(ex.Message));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing snapshot write request");
            return StatusCode(StatusCodes.Status500InternalServerError,
                ErrorEnvelope.Internal("An error occurred while processing your request"));
        }
    }

    /// <summary>
    /// Stateful read: returns the client's persisted snapshots as a chronological PD trajectory
    /// (oldest → newest) plus the current per-model trends (monitoring API contract 4.4).
    /// Optionally filtered by <c>from</c>/<c>to</c> dates and capped by <c>limit</c> (1..500).
    /// </summary>
    [HttpGet("clients/{clientRef}/history")]
    [ProducesResponseType(typeof(HistoryResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorEnvelope), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ErrorEnvelope), StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetClientHistory(
        string clientRef,
        [FromQuery] DateOnly? from,
        [FromQuery] DateOnly? to,
        [FromQuery] int limit = 100)
    {
        if (string.IsNullOrWhiteSpace(clientRef) || clientRef.Length > 64)
        {
            return BadRequest(ErrorEnvelope.ValidationFailed(
                "clientRef must be between 1 and 64 characters", new { field = "clientRef" }));
        }

        if (limit < 1 || limit > 500)
        {
            return BadRequest(ErrorEnvelope.ValidationFailed(
                "limit must be between 1 and 500", new { field = "limit" }));
        }

        if (from is { } f && to is { } t && f > t)
        {
            return BadRequest(ErrorEnvelope.ValidationFailed(
                "from must not be after to", new { field = "from" }));
        }

        try
        {
            _logger.LogInformation("Received history read request for client {ClientRef}", clientRef);
            var result = await _monitoringService.GetClientHistoryAsync(clientRef, from, to, limit);
            return Ok(result);
        }
        catch (ClientNotFoundException ex)
        {
            _logger.LogWarning(ex, "History requested for unknown client {ClientRef}", clientRef);
            return NotFound(ErrorEnvelope.ClientNotFound(ex.Message));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing history read request");
            return StatusCode(StatusCodes.Status500InternalServerError,
                ErrorEnvelope.Internal("An error occurred while processing your request"));
        }
    }
}
