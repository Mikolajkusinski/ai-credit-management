using System.Text.Json.Serialization;

namespace WebApi.Models;

/// <summary>
/// Trajectory scoring response (monitoring API contract 3.5). Doubles as the deserialization
/// target for the Flask <c>/predict/timeseries</c> response and as the public response body
/// (same pattern as <see cref="PredictResponse"/>). Flask returns <c>label</c> and
/// <c>snapshotDate</c> as null; the backend fills them in.
/// </summary>
public class TimeseriesResponse
{
    [JsonPropertyName("clientRef")]
    public string? ClientRef { get; set; }

    [JsonPropertyName("snapshotDate")]
    public DateOnly? SnapshotDate { get; set; }

    [JsonPropertyName("trajectory")]
    public List<TrajectoryPoint> Trajectory { get; set; } = new();

    [JsonPropertyName("trends")]
    public Trends Trends { get; set; } = new();
}

public class TrajectoryPoint
{
    [JsonPropertyName("window")]
    public string Window { get; set; } = string.Empty;

    /// <summary>Human-readable month range (e.g. "Mar-May 2026"); computed by the backend from snapshotDate.</summary>
    [JsonPropertyName("label")]
    public string? Label { get; set; }

    [JsonPropertyName("predictions")]
    public WindowPredictions Predictions { get; set; } = new();
}

public class WindowPredictions
{
    [JsonPropertyName("randomForest")]
    public double RandomForest { get; set; }

    [JsonPropertyName("xgboost")]
    public double Xgboost { get; set; }

    [JsonPropertyName("lstm")]
    public double Lstm { get; set; }
}

public class Trends
{
    [JsonPropertyName("randomForest")]
    public TrendInfo RandomForest { get; set; } = new();

    [JsonPropertyName("xgboost")]
    public TrendInfo Xgboost { get; set; } = new();

    [JsonPropertyName("lstm")]
    public TrendInfo Lstm { get; set; } = new();
}

public class TrendInfo
{
    /// <summary>PD_W3 − PD_W0, in [-1, +1].</summary>
    [JsonPropertyName("slope")]
    public double Slope { get; set; }

    /// <summary>"INCREASING_RISK" | "DECREASING_RISK" | "STABLE".</summary>
    [JsonPropertyName("alert")]
    public string Alert { get; set; } = string.Empty;
}
