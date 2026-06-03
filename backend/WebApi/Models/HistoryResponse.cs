using System.Text.Json.Serialization;

namespace WebApi.Models;

/// <summary>
/// Client monitoring history (monitoring API contract 4.4): the chronological timeline of real
/// snapshots submitted for a client, each carrying its persisted W3 predictions, plus the current
/// per-model trends. Reuses <see cref="WindowPredictions"/> and <see cref="Trends"/> from
/// <see cref="TimeseriesResponse"/> — the JSON shapes are identical to the contract.
/// </summary>
public class HistoryResponse
{
    [JsonPropertyName("clientRef")]
    public string ClientRef { get; set; } = string.Empty;

    /// <summary>When the client record was first created (ISO-8601 UTC).</summary>
    [JsonPropertyName("createdAt")]
    public DateTime CreatedAt { get; set; }

    /// <summary>Snapshots ordered oldest → newest (left = oldest for the trajectory chart).</summary>
    [JsonPropertyName("history")]
    public List<HistoryPoint> History { get; set; } = new();

    /// <summary>Current per-model trend, read from the persisted Trend rows (written by CREDIT-203).</summary>
    [JsonPropertyName("trends")]
    public Trends Trends { get; set; } = new();
}

public class HistoryPoint
{
    [JsonPropertyName("snapshotId")]
    public int SnapshotId { get; set; }

    [JsonPropertyName("snapshotDate")]
    public DateOnly SnapshotDate { get; set; }

    [JsonPropertyName("predictions")]
    public WindowPredictions Predictions { get; set; } = new();
}
