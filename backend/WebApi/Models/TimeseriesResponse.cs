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

    /// <summary>
    /// CREDIT-107/211: top-5 SHAP features per tree-based model for the W3 (latest) window.
    /// Computed by Flask at scoring time only; null when absent (older ML service) or on the
    /// history read path (SHAP is not persisted). LSTM is intentionally excluded (TreeExplainer
    /// only). Additive, non-breaking pass-through.
    /// </summary>
    [JsonPropertyName("shap")]
    public ShapExplanation? Shap { get; set; }
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

    /// <summary>CREDIT-109: LightGBM W3 calibrated prediction.</summary>
    [JsonPropertyName("lightgbm")]
    public double Lightgbm { get; set; }

    /// <summary>CREDIT-109: CatBoost W3 calibrated prediction.</summary>
    [JsonPropertyName("catboost")]
    public double Catboost { get; set; }

    [JsonPropertyName("lstm")]
    public double Lstm { get; set; }
}

public class Trends
{
    [JsonPropertyName("randomForest")]
    public TrendInfo RandomForest { get; set; } = new();

    [JsonPropertyName("xgboost")]
    public TrendInfo Xgboost { get; set; } = new();

    /// <summary>CREDIT-109: LightGBM slope + alert.</summary>
    [JsonPropertyName("lightgbm")]
    public TrendInfo Lightgbm { get; set; } = new();

    /// <summary>CREDIT-109: CatBoost slope + alert.</summary>
    [JsonPropertyName("catboost")]
    public TrendInfo Catboost { get; set; } = new();

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

/// <summary>
/// SHAP top-5 feature attributions for the W3 window (CREDIT-107/211). One block per tree-based
/// model; LSTM is intentionally absent. Mirrors the fixed-property shape of <see cref="Trends"/>.
/// </summary>
public class ShapExplanation
{
    /// <summary>Window the attributions were computed on (always "W3").</summary>
    [JsonPropertyName("window")]
    public string Window { get; set; } = string.Empty;

    [JsonPropertyName("randomForest")]
    public ShapModel? RandomForest { get; set; }

    [JsonPropertyName("xgboost")]
    public ShapModel? Xgboost { get; set; }

    [JsonPropertyName("lightgbm")]
    public ShapModel? Lightgbm { get; set; }

    [JsonPropertyName("catboost")]
    public ShapModel? Catboost { get; set; }
}

public class ShapModel
{
    /// <summary>Top features ordered by descending |value| (Flask returns 5).</summary>
    [JsonPropertyName("topFeatures")]
    public List<ShapFeature> TopFeatures { get; set; } = new();
}

public class ShapFeature
{
    [JsonPropertyName("feature")]
    public string Feature { get; set; } = string.Empty;

    /// <summary>Raw SHAP value: positive raises PD (toward DEFAULT), negative lowers it.</summary>
    [JsonPropertyName("value")]
    public double Value { get; set; }
}
