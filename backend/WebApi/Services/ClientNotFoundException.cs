namespace WebApi.Services;

/// <summary>
/// Raised when a client reference does not exist on the read path
/// (monitoring API contract 4.4). The controller maps this to <c>404 CLIENT_NOT_FOUND</c>.
/// </summary>
public class ClientNotFoundException : Exception
{
    public ClientNotFoundException(string message) : base(message) { }
}
