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
}
