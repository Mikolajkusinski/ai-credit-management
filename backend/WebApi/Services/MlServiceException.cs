namespace WebApi.Services;

/// <summary>
/// Raised when a call to the Flask ML service fails. <see cref="UpstreamStatusCode"/> is the
/// HTTP status Flask returned (e.g. 500) when it responded with an error, or <c>null</c> when
/// Flask could not be reached at all (connection refused, DNS failure, timeout). The controller
/// maps a non-null status to <c>502 ML_SERVICE_ERROR</c> and null to <c>503 ML_SERVICE_UNAVAILABLE</c>.
/// </summary>
public class MlServiceException : Exception
{
    public int? UpstreamStatusCode { get; }

    public MlServiceException(string message, int? upstreamStatusCode, Exception? inner = null)
        : base(message, inner)
    {
        UpstreamStatusCode = upstreamStatusCode;
    }
}
