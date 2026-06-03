namespace WebApi.Services;

/// <summary>
/// Raised when a snapshot already exists for the same <c>(clientRef, snapshotDate)</c>
/// (monitoring API contract 4.3, open question #2). The controller maps this to
/// <c>409 CONFLICT</c>.
/// </summary>
public class SnapshotConflictException : Exception
{
    public SnapshotConflictException(string message) : base(message) { }
}
