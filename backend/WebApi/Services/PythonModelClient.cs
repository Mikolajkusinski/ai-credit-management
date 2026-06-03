using System.Text;
using System.Text.Json;
using WebApi.Models;

namespace WebApi.Services;

public class PythonModelClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<PythonModelClient> _logger;
    private readonly string _flaskServiceUrl;

    public PythonModelClient(HttpClient httpClient, IConfiguration configuration, ILogger<PythonModelClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _flaskServiceUrl = configuration["FlaskServiceUrl"] ?? "http://localhost:5000";
    }

    public async Task<PredictResponse?> GetPredictionsAsync(FlaskPredictRequest request)
    {
        try
        {
            var json = JsonSerializer.Serialize(request);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            _logger.LogInformation("Calling Flask service at {Url}", $"{_flaskServiceUrl}/predict");
            var response = await _httpClient.PostAsync($"{_flaskServiceUrl}/predict", content);

            response.EnsureSuccessStatusCode();

            var responseContent = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Received response from Flask service");

            return JsonSerializer.Deserialize<PredictResponse>(responseContent);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling Flask service");
            throw;
        }
    }

    /// <summary>
    /// Calls the Flask sliding-window scoring endpoint (<c>/predict/timeseries</c>, CREDIT-104).
    /// Throws <see cref="MlServiceException"/> with the upstream status when Flask responds with
    /// an error, or with a null status when Flask cannot be reached.
    /// </summary>
    public async Task<TimeseriesResponse?> GetTimeseriesAsync(FlaskPredictRequest request)
    {
        var url = $"{_flaskServiceUrl}/predict/timeseries";
        HttpResponseMessage response;
        try
        {
            var json = JsonSerializer.Serialize(request);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            _logger.LogInformation("Calling Flask service at {Url}", url);
            response = await _httpClient.PostAsync(url, content);
        }
        catch (Exception ex)
        {
            // Connection refused / DNS / timeout — Flask is unreachable.
            _logger.LogError(ex, "Flask service unreachable at {Url}", url);
            throw new MlServiceException("ML service is unreachable", upstreamStatusCode: null, inner: ex);
        }

        if (!response.IsSuccessStatusCode)
        {
            var status = (int)response.StatusCode;
            _logger.LogError("Flask service returned {Status} from {Url}", status, url);
            throw new MlServiceException($"ML service returned status {status}", upstreamStatusCode: status);
        }

        var responseContent = await response.Content.ReadAsStringAsync();
        _logger.LogInformation("Received timeseries response from Flask service");
        return JsonSerializer.Deserialize<TimeseriesResponse>(responseContent);
    }
}
