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
}
