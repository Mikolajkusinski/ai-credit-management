using System.Text.Json.Serialization;

namespace WebApi.Models;

/// <summary>
/// Common error format for 4xx/5xx responses (monitoring API contract 3.6).
/// </summary>
public class ErrorEnvelope
{
    [JsonPropertyName("error")]
    public ErrorBody Error { get; set; } = new();

    public ErrorEnvelope() { }

    public ErrorEnvelope(string code, string message, object? details = null)
    {
        Error = new ErrorBody { Code = code, Message = message, Details = details };
    }

    public static ErrorEnvelope ValidationFailed(string message, object? details = null) =>
        new("VALIDATION_FAILED", message, details);

    public static ErrorEnvelope MlServiceError(string message) =>
        new("ML_SERVICE_ERROR", message);

    public static ErrorEnvelope MlServiceUnavailable(string message) =>
        new("ML_SERVICE_UNAVAILABLE", message);

    public static ErrorEnvelope Internal(string message) =>
        new("INTERNAL_ERROR", message);
}

public class ErrorBody
{
    [JsonPropertyName("code")]
    public string Code { get; set; } = string.Empty;

    [JsonPropertyName("message")]
    public string Message { get; set; } = string.Empty;

    [JsonPropertyName("details")]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public object? Details { get; set; }
}
