using System.ComponentModel.DataAnnotations;

namespace WebApi.Models;

/// <summary>
/// Request for <c>POST /api/v1/monitoring/predict-timeseries</c> (monitoring API contract 4.2).
/// Stateless: <see cref="ClientRef"/> is echoed back only, nothing is persisted.
/// </summary>
public class TimeseriesRequest
{
    /// <summary>Optional business key — echoed into the response, never stored by this endpoint.</summary>
    public string? ClientRef { get; set; }

    /// <summary>Optional snapshot date used to compute window labels. Defaults to today (UTC) when omitted.</summary>
    public DateOnly? SnapshotDate { get; set; }

    [Required]
    public Snapshot22Features Features { get; set; } = new();
}
