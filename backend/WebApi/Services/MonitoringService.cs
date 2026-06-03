using System.Globalization;
using WebApi.Models;

namespace WebApi.Services;

/// <summary>
/// Orchestrates stateless trajectory scoring for <c>POST /api/v1/monitoring/predict-timeseries</c>:
/// maps the 22 features to the Flask request, calls the ML service, then enriches the response
/// with the echoed client reference, the resolved snapshot date, and per-window labels.
/// Trends are passed through from Flask (it owns the slope/alert rule — contract 4.1).
/// </summary>
public class MonitoringService
{
    private readonly PythonModelClient _pythonModelClient;
    private readonly ILogger<MonitoringService> _logger;

    // Number of months before the snapshot month that each window's FIRST month sits at
    // (contract 2.1/2.2). Window spans 3 consecutive months: first .. first+2.
    private static readonly Dictionary<string, int> FirstMonthOffset = new()
    {
        ["W0"] = 5,
        ["W1"] = 4,
        ["W2"] = 3,
        ["W3"] = 2,
    };

    public MonitoringService(PythonModelClient pythonModelClient, ILogger<MonitoringService> logger)
    {
        _pythonModelClient = pythonModelClient;
        _logger = logger;
    }

    public async Task<TimeseriesResponse?> PredictTimeseriesAsync(TimeseriesRequest request)
    {
        var flaskRequest = MapToFlaskRequest(request.Features);

        _logger.LogInformation("Sending timeseries request to Python service");
        var result = await _pythonModelClient.GetTimeseriesAsync(flaskRequest);
        if (result == null)
        {
            return null;
        }

        var snapshotDate = request.SnapshotDate ?? DateOnly.FromDateTime(DateTime.UtcNow);

        // Enrich the Flask response: Flask leaves clientRef/snapshotDate/labels empty by design.
        result.ClientRef = request.ClientRef;
        result.SnapshotDate = snapshotDate;
        foreach (var point in result.Trajectory)
        {
            point.Label = ComputeLabel(snapshotDate, point.Window);
        }

        return result;
    }

    /// <summary>
    /// Builds the "MMM-MMM yyyy" label (e.g. "Mar-May 2026") for a window, given the snapshot date.
    /// Returns null for an unknown window name (defensive — Flask only emits W0..W3).
    /// </summary>
    internal static string? ComputeLabel(DateOnly snapshotDate, string window)
    {
        if (!FirstMonthOffset.TryGetValue(window, out var offset))
        {
            return null;
        }

        var first = snapshotDate.AddMonths(-offset);
        var last = first.AddMonths(2);
        var firstAbbr = first.ToString("MMM", CultureInfo.InvariantCulture);
        var lastAbbr = last.ToString("MMM", CultureInfo.InvariantCulture);
        return $"{firstAbbr}-{lastAbbr} {last.Year}";
    }

    private static FlaskPredictRequest MapToFlaskRequest(Snapshot22Features f) => new()
    {
        LimitBal = f.LimitBal,
        Sex = f.Sex,
        Education = f.Education,
        Marriage = f.Marriage,
        Age = f.Age,
        Pay0 = f.Pay0,
        Pay2 = f.Pay2,
        Pay3 = f.Pay3,
        Pay4 = f.Pay4,
        Pay5 = f.Pay5,
        Pay6 = f.Pay6,
        BillAmt1 = f.BillAmt1,
        BillAmt2 = f.BillAmt2,
        BillAmt3 = f.BillAmt3,
        BillAmt4 = f.BillAmt4,
        BillAmt5 = f.BillAmt5,
        BillAmt6 = f.BillAmt6,
        PayAmt1 = f.PayAmt1,
        PayAmt2 = f.PayAmt2,
        PayAmt3 = f.PayAmt3,
        PayAmt4 = f.PayAmt4,
        PayAmt5 = f.PayAmt5,
        PayAmt6 = f.PayAmt6,
    };
}
