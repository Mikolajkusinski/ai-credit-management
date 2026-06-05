using System.Text.Json.Serialization;

namespace WebApi.Models;

/// <summary>
/// Response body for <c>POST /api/v1/monitoring/clients/{ref}/snapshots</c> (monitoring API
/// contract 4.3). Carries the scored trajectory (reusing the <see cref="TimeseriesResponse"/>
/// types) plus the ids of what was written to Postgres.
/// </summary>
public class SnapshotResponse
{
    [JsonPropertyName("snapshotId")]
    public int SnapshotId { get; set; }

    [JsonPropertyName("clientRef")]
    public string ClientRef { get; set; } = string.Empty;

    [JsonPropertyName("snapshotDate")]
    public DateOnly SnapshotDate { get; set; }

    [JsonPropertyName("trajectory")]
    public List<TrajectoryPoint> Trajectory { get; set; } = new();

    [JsonPropertyName("trends")]
    public Trends Trends { get; set; } = new();

    [JsonPropertyName("persisted")]
    public PersistedInfo Persisted { get; set; } = new();
}

public class PersistedInfo
{
    /// <summary>True when the client was auto-created by this request; false when it already existed.</summary>
    [JsonPropertyName("clientCreated")]
    public bool ClientCreated { get; set; }

    /// <summary>Ids of the 5 persisted W3 predictions (one per model: RF, XGB, LightGBM, CatBoost, LSTM — CREDIT-109).</summary>
    [JsonPropertyName("predictionIds")]
    public List<int> PredictionIds { get; set; } = new();

    /// <summary>Ids of the 5 upserted trends (one per model: RF, XGB, LightGBM, CatBoost, LSTM — CREDIT-109).</summary>
    [JsonPropertyName("trendIds")]
    public List<int> TrendIds { get; set; } = new();
}
