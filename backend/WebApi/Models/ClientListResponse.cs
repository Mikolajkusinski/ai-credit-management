using System.Text.Json.Serialization;

namespace WebApi.Models;

/// <summary>
/// Monitored-client roster (monitoring API contract 4.5): every client that has a persisted record,
/// with just enough per-client stats to drive the CREDIT-302 client list — the count of snapshots,
/// the date of the latest one, and a single roll-up alert badge. Clicking a row loads that client's
/// full timeline via <c>GET clients/{ref}/history</c> (contract 4.4 / <see cref="HistoryResponse"/>).
/// </summary>
public class ClientListResponse
{
    [JsonPropertyName("clients")]
    public List<ClientSummary> Clients { get; set; } = new();
}

public class ClientSummary
{
    [JsonPropertyName("clientRef")]
    public string ClientRef { get; set; } = string.Empty;

    /// <summary>When the client record was first created (ISO-8601 UTC).</summary>
    [JsonPropertyName("createdAt")]
    public DateTime CreatedAt { get; set; }

    /// <summary>Number of persisted snapshots for this client.</summary>
    [JsonPropertyName("snapshotCount")]
    public int SnapshotCount { get; set; }

    /// <summary>Date of the most recent snapshot; null when the client has none yet.</summary>
    [JsonPropertyName("latestSnapshotDate")]
    public DateOnly? LatestSnapshotDate { get; set; }

    /// <summary>
    /// Single roll-up of the per-model trends for the list badge: <c>INCREASING_RISK</c> if any
    /// model flags rising risk, else <c>DECREASING_RISK</c> if any model is falling, else
    /// <c>STABLE</c>. The per-model breakdown is on the history view.
    /// </summary>
    [JsonPropertyName("latestAlert")]
    public string LatestAlert { get; set; } = "STABLE";
}
