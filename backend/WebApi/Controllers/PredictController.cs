using Microsoft.AspNetCore.Mvc;
using WebApi.Models;
using WebApi.Services;

namespace WebApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PredictController : ControllerBase
{
    private readonly PredictionService _predictionService;
    private readonly ILogger<PredictController> _logger;

    public PredictController(PredictionService predictionService, ILogger<PredictController> logger)
    {
        _predictionService = predictionService;
        _logger = logger;
    }

    /// <summary>
    /// Predicts credit card default risk using multiple ML models
    /// </summary>
    /// <param name="request">Credit card holder information</param>
    /// <returns>Predictions from Random Forest, XGBoost, and LSTM models</returns>
    [HttpPost]
    [ProducesResponseType(typeof(PredictResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<PredictResponse>> Predict([FromBody] PredictRequest request)
    {
        try
        {
            _logger.LogInformation("Received prediction request");
            var result = await _predictionService.PredictAsync(request);

            if (result == null)
            {
                return StatusCode(500, "Failed to get predictions from ML service");
            }

            return Ok(result);
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Validation error");
            return BadRequest(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing prediction request");
            return StatusCode(500, new { error = "An error occurred while processing your request" });
        }
    }
}
