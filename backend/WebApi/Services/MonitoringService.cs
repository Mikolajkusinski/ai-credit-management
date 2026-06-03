using System.Globalization;
using WebApi.Models;
using WebApi.Models.Entities;

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
    private readonly SnapshotRepository _snapshotRepository;
    private readonly PredictionRepository _predictionRepository;
    private readonly TrendRepository _trendRepository;
    private readonly ILogger<MonitoringService> _logger;

    // The labelled window whose predictions are persisted (contract open question #1 = W3 only).
    private const string LabelledWindow = "W3";

    // Number of months before the snapshot month that each window's FIRST month sits at
    // (contract 2.1/2.2). Window spans 3 consecutive months: first .. first+2.
    private static readonly Dictionary<string, int> FirstMonthOffset = new()
    {
        ["W0"] = 5,
        ["W1"] = 4,
        ["W2"] = 3,
        ["W3"] = 2,
    };

    public MonitoringService(
        PythonModelClient pythonModelClient,
        SnapshotRepository snapshotRepository,
        PredictionRepository predictionRepository,
        TrendRepository trendRepository,
        ILogger<MonitoringService> logger)
    {
        _pythonModelClient = pythonModelClient;
        _snapshotRepository = snapshotRepository;
        _predictionRepository = predictionRepository;
        _trendRepository = trendRepository;
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
    /// Stateful write path for <c>POST /api/v1/monitoring/clients/{ref}/snapshots</c> (contract 4.3):
    /// validates duplicates, scores via Flask (reusing <see cref="PredictTimeseriesAsync"/>), then
    /// persists the snapshot, its W3 predictions, and the per-model trends.
    /// </summary>
    /// <exception cref="SnapshotConflictException">The client already has a snapshot on that date.</exception>
    /// <exception cref="MlServiceException">Flask could not be reached or returned an error.</exception>
    public async Task<SnapshotResponse> ScoreAndPersistAsync(string clientRef, SnapshotRequest request)
    {
        var snapshotDate = request.SnapshotDate ?? DateOnly.FromDateTime(DateTime.UtcNow);

        // Reject duplicates before scoring so Flask isn't called and no client is created on conflict.
        var client = await _snapshotRepository.FindClientAsync(clientRef);
        if (client is not null && await _snapshotRepository.ExistsForDateAsync(client.Id, snapshotDate))
        {
            throw new SnapshotConflictException(
                $"A snapshot for client '{clientRef}' on {snapshotDate:yyyy-MM-dd} already exists");
        }

        // Score (clientRef/snapshotDate/labels are filled in by PredictTimeseriesAsync).
        var scored = await PredictTimeseriesAsync(new TimeseriesRequest
        {
            ClientRef = clientRef,
            SnapshotDate = snapshotDate,
            Features = request.Features,
        });
        if (scored is null)
        {
            throw new MlServiceException("ML service returned an empty response", upstreamStatusCode: null);
        }

        var clientCreated = client is null;
        client ??= await _snapshotRepository.CreateClientAsync(clientRef);

        // Persist the snapshot (SnapshotDate column is timestamptz → Kind must be Utc).
        var snapshot = await _snapshotRepository.AddAsync(MapToSnapshot(
            client.Id, snapshotDate.ToDateTime(TimeOnly.MinValue, DateTimeKind.Utc), request.Features));

        // Persist the W3 predictions (one row per model).
        var w3 = scored.Trajectory.First(p => p.Window == LabelledWindow).Predictions;
        var predictions = await _predictionRepository.AddRangeAsync(snapshot.Id, new[]
        {
            ToPrediction("randomForest", w3.RandomForest),
            ToPrediction("xgboost", w3.Xgboost),
            ToPrediction("lstm", w3.Lstm),
        });

        // Upsert the per-model trends.
        var trends = await _trendRepository.UpsertRangeAsync(client.Id, new[]
        {
            ("randomForest", scored.Trends.RandomForest.Slope, scored.Trends.RandomForest.Alert),
            ("xgboost", scored.Trends.Xgboost.Slope, scored.Trends.Xgboost.Alert),
            ("lstm", scored.Trends.Lstm.Slope, scored.Trends.Lstm.Alert),
        });

        _logger.LogInformation(
            "Persisted snapshot {SnapshotId} for client {ClientRef} ({PredCount} predictions, {TrendCount} trends)",
            snapshot.Id, clientRef, predictions.Count, trends.Count);

        return new SnapshotResponse
        {
            SnapshotId = snapshot.Id,
            ClientRef = clientRef,
            SnapshotDate = snapshotDate,
            Trajectory = scored.Trajectory,
            Trends = scored.Trends,
            Persisted = new PersistedInfo
            {
                ClientCreated = clientCreated,
                PredictionIds = predictions.Select(p => p.Id).ToList(),
                TrendIds = trends.Select(t => t.Id).ToList(),
            },
        };
    }

    /// <summary>
    /// Read path for <c>GET /api/v1/monitoring/clients</c> (contract 4.5): lists every persisted client
    /// with its snapshot count, latest snapshot date, and a single roll-up alert. Ordered by most-recent
    /// activity (clients with snapshots first, newest snapshot first), then by creation date. Pure read.
    /// </summary>
    public async Task<ClientListResponse> GetClientsAsync()
    {
        var rows = await _snapshotRepository.GetClientStatsAsync();

        var clients = rows
            .Select(r => new ClientSummary
            {
                ClientRef = r.ExternalRef,
                CreatedAt = r.CreatedAt,
                SnapshotCount = r.SnapshotCount,
                LatestSnapshotDate = r.LatestSnapshotDate is { } d ? DateOnly.FromDateTime(d) : null,
                LatestAlert = RollUpAlert(r.Alerts),
            })
            .OrderByDescending(c => c.LatestSnapshotDate.HasValue)
            .ThenByDescending(c => c.LatestSnapshotDate)
            .ThenByDescending(c => c.CreatedAt)
            .ToList();

        _logger.LogInformation("Listed {Count} monitored client(s)", clients.Count);
        return new ClientListResponse { Clients = clients };
    }

    // Surfaces the most actionable signal for the list badge: rising risk wins over falling, which
    // wins over stable. STABLE when a client has no stored trends yet.
    private static string RollUpAlert(IReadOnlyCollection<string> alerts)
    {
        if (alerts.Contains("INCREASING_RISK")) return "INCREASING_RISK";
        if (alerts.Contains("DECREASING_RISK")) return "DECREASING_RISK";
        return "STABLE";
    }

    /// <summary>
    /// Read path for <c>GET /api/v1/monitoring/clients/{ref}/history</c> (contract 4.4): assembles
    /// the client's persisted snapshots (with W3 predictions) into a chronological PD trajectory and
    /// attaches the current per-model trends. Pure read — no Flask call, no writes.
    /// </summary>
    /// <exception cref="ClientNotFoundException">The client reference does not exist.</exception>
    public async Task<HistoryResponse> GetClientHistoryAsync(string clientRef, DateOnly? from, DateOnly? to, int limit)
    {
        var client = await _snapshotRepository.FindClientAsync(clientRef)
            ?? throw new ClientNotFoundException($"Client '{clientRef}' does not exist");

        var snapshots = await _snapshotRepository.GetHistoryAsync(client.Id, from, to, limit);
        var trends = await _trendRepository.GetByClientAsync(client.Id);

        _logger.LogInformation(
            "Read history for client {ClientRef}: {Count} snapshot(s)", clientRef, snapshots.Count);

        return new HistoryResponse
        {
            ClientRef = clientRef,
            CreatedAt = client.CreatedAt,
            History = snapshots.Select(MapHistoryPoint).ToList(),
            Trends = MapTrends(trends),
        };
    }

    private static HistoryPoint MapHistoryPoint(Snapshot s) => new()
    {
        SnapshotId = s.Id,
        SnapshotDate = DateOnly.FromDateTime(s.SnapshotDate),
        Predictions = new WindowPredictions
        {
            RandomForest = ProbabilityFor(s.Predictions, "randomForest"),
            Xgboost = ProbabilityFor(s.Predictions, "xgboost"),
            Lstm = ProbabilityFor(s.Predictions, "lstm"),
        },
    };

    private static double ProbabilityFor(IEnumerable<Prediction> predictions, string modelName) =>
        predictions.FirstOrDefault(p => p.ModelName == modelName)?.DefaultProbability ?? 0d;

    private static Trends MapTrends(IReadOnlyCollection<Trend> trends) => new()
    {
        RandomForest = TrendInfoFor(trends, "randomForest"),
        Xgboost = TrendInfoFor(trends, "xgboost"),
        Lstm = TrendInfoFor(trends, "lstm"),
    };

    // Falls back to a neutral STABLE trend when a model has no stored row (e.g. a client with no snapshots).
    private static TrendInfo TrendInfoFor(IEnumerable<Trend> trends, string modelName)
    {
        var row = trends.FirstOrDefault(t => t.ModelName == modelName);
        return row is null
            ? new TrendInfo { Slope = 0d, Alert = "STABLE" }
            : new TrendInfo { Slope = row.Slope, Alert = row.Alert };
    }

    private static Prediction ToPrediction(string modelName, double pd) => new()
    {
        ModelName = modelName,
        DefaultProbability = pd,
        Label = pd >= 0.5 ? "DEFAULT" : "NO DEFAULT",
    };

    private static Snapshot MapToSnapshot(int clientId, DateTime snapshotDate, Snapshot22Features f) => new()
    {
        ClientId = clientId,
        SnapshotDate = snapshotDate,
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
