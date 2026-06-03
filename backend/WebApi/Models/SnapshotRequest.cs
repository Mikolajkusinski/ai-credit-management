using System.ComponentModel.DataAnnotations;

namespace WebApi.Models;

/// <summary>
/// Request body for <c>POST /api/v1/monitoring/clients/{ref}/snapshots</c> (monitoring API
/// contract 4.3). The client business key arrives as the <c>{ref}</c> path parameter, so — unlike
/// <see cref="TimeseriesRequest"/> — this body carries no <c>clientRef</c>.
/// </summary>
public class SnapshotRequest
{
    /// <summary>Optional snapshot date. Defaults to today (UTC) when omitted. Must not be in the future.</summary>
    public DateOnly? SnapshotDate { get; set; }

    [Required]
    public Snapshot22Features Features { get; set; } = new();
}
