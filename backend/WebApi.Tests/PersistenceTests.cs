using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Testcontainers.PostgreSql;
using WebApi.Data;
using WebApi.Models;
using WebApi.Models.Entities;
using WebApi.Services;

namespace WebApi.Tests;

/// <summary>
/// Faithful relational persistence suite (CREDIT-205). Unlike the EF Core in-memory tests
/// (<see cref="SnapshotPersistenceTests"/>, <see cref="ClientHistoryTests"/>), these run the real Npgsql
/// migration against a throw-away PostgreSQL 16 container, so they exercise what in-memory cannot:
/// the unique <c>ExternalRef</c> index, FK <c>ON DELETE CASCADE</c>, the <c>(ClientId, ModelName)</c>
/// trend upsert key, <c>timestamptz</c> round-tripping, and <c>NOW()</c> server defaults.
///
/// The Flask call is still stubbed via an <see cref="HttpMessageHandler"/> — only the database is real.
/// The container is shared across the class (one instance) and each test starts from a truncated schema.
/// </summary>
[Collection(PostgresCollection.Name)]
public class PersistenceTests : IAsyncLifetime
{
    private readonly PostgresFixture _fixture;

    public PersistenceTests(PostgresFixture fixture) => _fixture = fixture;

    // Reset to an empty (but migrated) schema before every test. RESTART IDENTITY keeps ids predictable;
    // CASCADE also exercises the real FK wiring as a side effect.
    public async Task InitializeAsync()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseNpgsql(_fixture.ConnectionString)
            .Options;
        await using var db = new AppDbContext(options);
        await db.Database.ExecuteSqlRawAsync(
            """TRUNCATE "Clients", "Snapshots", "Predictions", "Trends" RESTART IDENTITY CASCADE;""");
    }

    public Task DisposeAsync() => Task.CompletedTask;

    // Contract-shaped Flask /predict/timeseries response: increasing trends, W3 = 0.58/0.61/0.55.
    private const string FlaskIncreasingBody = """
    {
      "snapshotDate": null,
      "trajectory": [
        { "window": "W0", "label": null, "predictions": { "randomForest": 0.18, "xgboost": 0.20, "lstm": 0.15 } },
        { "window": "W1", "label": null, "predictions": { "randomForest": 0.27, "xgboost": 0.29, "lstm": 0.24 } },
        { "window": "W2", "label": null, "predictions": { "randomForest": 0.41, "xgboost": 0.44, "lstm": 0.39 } },
        { "window": "W3", "label": null, "predictions": { "randomForest": 0.58, "xgboost": 0.61, "lstm": 0.55 } }
      ],
      "trends": {
        "randomForest": { "slope": 0.40, "alert": "INCREASING_RISK" },
        "xgboost":      { "slope": 0.41, "alert": "INCREASING_RISK" },
        "lstm":         { "slope": 0.40, "alert": "INCREASING_RISK" }
      }
    }
    """;

    // A contrasting response used to prove trend upsert (overwrite, not append): falling risk, W3 < 0.5.
    private const string FlaskDecreasingBody = """
    {
      "snapshotDate": null,
      "trajectory": [
        { "window": "W0", "label": null, "predictions": { "randomForest": 0.52, "xgboost": 0.55, "lstm": 0.50 } },
        { "window": "W1", "label": null, "predictions": { "randomForest": 0.40, "xgboost": 0.43, "lstm": 0.38 } },
        { "window": "W2", "label": null, "predictions": { "randomForest": 0.30, "xgboost": 0.33, "lstm": 0.28 } },
        { "window": "W3", "label": null, "predictions": { "randomForest": 0.22, "xgboost": 0.25, "lstm": 0.20 } }
      ],
      "trends": {
        "randomForest": { "slope": -0.30, "alert": "DECREASING_RISK" },
        "xgboost":      { "slope": -0.30, "alert": "DECREASING_RISK" },
        "lstm":         { "slope": -0.30, "alert": "DECREASING_RISK" }
      }
    }
    """;

    private WebApplicationFactory<Program> CreateFactory(Func<HttpRequestMessage, HttpResponseMessage> responder)
    {
        return new WebApplicationFactory<Program>().WithWebHostBuilder(builder =>
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureTestServices(services =>
            {
                services.AddHttpClient<PythonModelClient>()
                    .ConfigurePrimaryHttpMessageHandler(() => new StubHttpMessageHandler(responder));

                // Swap the configured PostgreSQL for the throw-away container's database.
                services.RemoveAll(typeof(DbContextOptions<AppDbContext>));
                services.AddDbContext<AppDbContext>(o => o.UseNpgsql(_fixture.ConnectionString));
            });
        });
    }

    private WebApplicationFactory<Program> CreateFactory(string flaskBody = FlaskIncreasingBody) =>
        CreateFactory(_ => JsonResponse(HttpStatusCode.OK, flaskBody));

    private AppDbContext NewDbContext(WebApplicationFactory<Program> factory) =>
        factory.Services.CreateScope().ServiceProvider.GetRequiredService<AppDbContext>();

    private static object ValidFeatures(int age = 35) => new
    {
        limitBal = 100000,
        sex = 1,
        education = 2,
        marriage = 1,
        age,
        pay0 = 0, pay2 = 0, pay3 = 0, pay4 = 0, pay5 = 0, pay6 = 0,
        billAmt1 = 50000, billAmt2 = 48000, billAmt3 = 46000,
        billAmt4 = 44000, billAmt5 = 42000, billAmt6 = 40000,
        payAmt1 = 5000, payAmt2 = 5000, payAmt3 = 5000,
        payAmt4 = 5000, payAmt5 = 5000, payAmt6 = 5000
    };

    private static async Task PostSnapshot(HttpClient client, string clientRef, string date)
    {
        var response = await client.PostAsJsonAsync(
            $"/api/v1/monitoring/clients/{clientRef}/snapshots",
            new { snapshotDate = date, features = ValidFeatures() });
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    }

    [Fact]
    public async Task WriteReadRoundTrip_PersistsAllRows_AndHistoryReturnsPoint()
    {
        await using var factory = CreateFactory();
        var client = factory.CreateClient();

        var response = await client.PostAsJsonAsync("/api/v1/monitoring/clients/rt-client/snapshots", new
        {
            snapshotDate = "2026-05-10",
            features = ValidFeatures()
        });
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);

        var body = await response.Content.ReadFromJsonAsync<SnapshotResponse>();
        Assert.NotNull(body);
        Assert.True(body!.Persisted.ClientCreated);
        Assert.Equal(3, body.Persisted.PredictionIds.Count);
        Assert.Equal(3, body.Persisted.TrendIds.Count);

        // Rows landed in real PostgreSQL.
        using (var db = NewDbContext(factory))
        {
            var dbClient = Assert.Single(await db.Clients.ToListAsync());
            Assert.Equal("rt-client", dbClient.ExternalRef);

            var snapshot = Assert.Single(await db.Snapshots.ToListAsync());
            Assert.Equal(dbClient.Id, snapshot.ClientId);
            Assert.Equal(body.SnapshotId, snapshot.Id);
            Assert.Equal(100000, snapshot.LimitBal);

            var predictions = await db.Predictions.ToListAsync();
            Assert.Equal(3, predictions.Count);
            Assert.All(predictions, p => Assert.Equal(snapshot.Id, p.SnapshotId));
            var rf = Assert.Single(predictions, p => p.ModelName == "randomForest");
            Assert.Equal(0.58, rf.DefaultProbability, 3);
            Assert.Equal("DEFAULT", rf.Label);

            var trends = await db.Trends.ToListAsync();
            Assert.Equal(3, trends.Count);
            Assert.All(trends, t => Assert.Equal(dbClient.Id, t.ClientId));
            Assert.All(trends, t => Assert.Equal("INCREASING_RISK", t.Alert));
        }

        // And the read path returns it.
        var history = await client.GetFromJsonAsync<HistoryResponse>(
            "/api/v1/monitoring/clients/rt-client/history");
        var point = Assert.Single(history!.History);
        Assert.Equal(new DateOnly(2026, 5, 10), point.SnapshotDate);
        Assert.Equal(0.58, point.Predictions.RandomForest, 3);
        Assert.Equal("INCREASING_RISK", history.Trends.RandomForest.Alert);
    }

    [Fact]
    public async Task MultipleSnapshots_HistoryReturnsPointsAscendingByDate()
    {
        await using var factory = CreateFactory();
        var client = factory.CreateClient();

        // Posted out of order — real SQL ordering must return them ascending.
        await PostSnapshot(client, "asc-client", "2026-05-24");
        await PostSnapshot(client, "asc-client", "2026-04-15");
        await PostSnapshot(client, "asc-client", "2026-05-10");

        var history = await client.GetFromJsonAsync<HistoryResponse>(
            "/api/v1/monitoring/clients/asc-client/history");
        Assert.Equal(3, history!.History.Count);
        Assert.Equal(new DateOnly(2026, 4, 15), history.History[0].SnapshotDate);
        Assert.Equal(new DateOnly(2026, 5, 10), history.History[1].SnapshotDate);
        Assert.Equal(new DateOnly(2026, 5, 24), history.History[2].SnapshotDate);

        // One client, three snapshots, trends upserted (not duplicated).
        using var db = NewDbContext(factory);
        Assert.Single(await db.Clients.ToListAsync());
        Assert.Equal(3, await db.Snapshots.CountAsync());
        Assert.Equal(3, await db.Trends.CountAsync());
    }

    [Fact]
    public async Task CascadeDelete_RemovingClient_RemovesSnapshotsPredictionsAndTrends()
    {
        await using var factory = CreateFactory();
        var client = factory.CreateClient();

        await PostSnapshot(client, "cascade-client", "2026-05-10");
        await PostSnapshot(client, "cascade-client", "2026-04-15");

        // Sanity: children exist before delete.
        using (var db = NewDbContext(factory))
        {
            Assert.Equal(2, await db.Snapshots.CountAsync());
            Assert.Equal(6, await db.Predictions.CountAsync());
            Assert.Equal(3, await db.Trends.CountAsync());
        }

        // Delete only the parent; the DB-enforced ON DELETE CASCADE must remove every child.
        using (var db = NewDbContext(factory))
        {
            var dbClient = await db.Clients.SingleAsync(c => c.ExternalRef == "cascade-client");
            db.Clients.Remove(dbClient);
            await db.SaveChangesAsync();
        }

        using (var db = NewDbContext(factory))
        {
            Assert.Empty(await db.Clients.ToListAsync());
            Assert.Empty(await db.Snapshots.ToListAsync());
            Assert.Empty(await db.Predictions.ToListAsync());
            Assert.Empty(await db.Trends.ToListAsync());
        }
    }

    [Fact]
    public async Task UniqueExternalRef_SameClientTwoSnapshots_CreatesOneClientRow()
    {
        await using var factory = CreateFactory();
        var client = factory.CreateClient();

        var first = await client.PostAsJsonAsync("/api/v1/monitoring/clients/unique-client/snapshots",
            new { snapshotDate = "2026-04-15", features = ValidFeatures() });
        Assert.Equal(HttpStatusCode.Created, first.StatusCode);
        var firstBody = await first.Content.ReadFromJsonAsync<SnapshotResponse>();
        Assert.True(firstBody!.Persisted.ClientCreated);

        var second = await client.PostAsJsonAsync("/api/v1/monitoring/clients/unique-client/snapshots",
            new { snapshotDate = "2026-05-10", features = ValidFeatures() });
        Assert.Equal(HttpStatusCode.Created, second.StatusCode);
        var secondBody = await second.Content.ReadFromJsonAsync<SnapshotResponse>();
        Assert.False(secondBody!.Persisted.ClientCreated);

        using var db = NewDbContext(factory);
        var dbClient = Assert.Single(await db.Clients.ToListAsync());  // unique index honoured
        Assert.Equal("unique-client", dbClient.ExternalRef);
        Assert.Equal(2, await db.Snapshots.CountAsync());
    }

    [Fact]
    public async Task TrendUpsert_SecondSnapshot_UpdatesRowsInPlace_AndBumpsComputedAt()
    {
        // First snapshot scores INCREASING_RISK, the second DECREASING_RISK.
        var bodies = new Queue<string>(new[] { FlaskIncreasingBody, FlaskDecreasingBody });
        await using var factory = CreateFactory(_ => JsonResponse(HttpStatusCode.OK, bodies.Dequeue()));
        var client = factory.CreateClient();

        await PostSnapshot(client, "upsert-client", "2026-04-15");

        DateTime firstComputedAt;
        using (var db = NewDbContext(factory))
        {
            var rf = await db.Trends.SingleAsync(t => t.ModelName == "randomForest");
            Assert.Equal("INCREASING_RISK", rf.Alert);
            Assert.Equal(0.40, rf.Slope, 3);
            firstComputedAt = rf.ComputedAt;
        }

        await PostSnapshot(client, "upsert-client", "2026-05-10");

        using (var db = NewDbContext(factory))
        {
            // Still exactly one trend row per model for the client — updated, not appended.
            Assert.Equal(3, await db.Trends.CountAsync());
            var rf = await db.Trends.SingleAsync(t => t.ModelName == "randomForest");
            Assert.Equal("DECREASING_RISK", rf.Alert);
            Assert.Equal(-0.30, rf.Slope, 3);
            Assert.True(rf.ComputedAt >= firstComputedAt, "ComputedAt should advance on upsert");
        }
    }

    [Fact]
    public async Task DuplicateDate_Returns409Conflict_AndOnlyFirstWritePersists()
    {
        await using var factory = CreateFactory();
        var client = factory.CreateClient();

        object payload = new { snapshotDate = "2026-05-10", features = ValidFeatures() };

        var first = await client.PostAsJsonAsync("/api/v1/monitoring/clients/dup-client/snapshots", payload);
        Assert.Equal(HttpStatusCode.Created, first.StatusCode);

        var second = await client.PostAsJsonAsync("/api/v1/monitoring/clients/dup-client/snapshots", payload);
        Assert.Equal(HttpStatusCode.Conflict, second.StatusCode);
        var error = await second.Content.ReadFromJsonAsync<ErrorEnvelope>();
        Assert.Equal("CONFLICT", error!.Error.Code);

        using var db = NewDbContext(factory);
        Assert.Single(await db.Snapshots.ToListAsync());
        Assert.Equal(3, await db.Predictions.CountAsync());
    }

    [Fact]
    public async Task SnapshotDate_StoredAsUtcTimestamptz_RoundTripsToDateOnly()
    {
        await using var factory = CreateFactory();
        var client = factory.CreateClient();

        await PostSnapshot(client, "tz-client", "2026-05-10");

        using (var db = NewDbContext(factory))
        {
            var snapshot = Assert.Single(await db.Snapshots.ToListAsync());
            // Npgsql reads `timestamp with time zone` back as a UTC DateTime.
            Assert.Equal(DateTimeKind.Utc, snapshot.SnapshotDate.Kind);
            Assert.Equal(new DateTime(2026, 5, 10, 0, 0, 0, DateTimeKind.Utc), snapshot.SnapshotDate);
        }

        var history = await client.GetFromJsonAsync<HistoryResponse>(
            "/api/v1/monitoring/clients/tz-client/history");
        Assert.Equal(new DateOnly(2026, 5, 10), Assert.Single(history!.History).SnapshotDate);
    }

    [Fact]
    public async Task ServerDefaults_PopulateCreatedAtAndComputedAt_FromNow()
    {
        var before = DateTime.UtcNow.AddMinutes(-1);
        await using var factory = CreateFactory();
        var client = factory.CreateClient();

        await PostSnapshot(client, "defaults-client", "2026-05-10");

        using var db = NewDbContext(factory);
        // HasDefaultValueSql("NOW()") — populated by the server, which the in-memory provider ignores.
        var dbClient = Assert.Single(await db.Clients.ToListAsync());
        Assert.NotEqual(default, dbClient.CreatedAt);
        Assert.True(dbClient.CreatedAt >= before, "CreatedAt should be set by the DB NOW() default");

        var trend = await db.Trends.FirstAsync();
        Assert.NotEqual(default, trend.ComputedAt);
        Assert.True(trend.ComputedAt >= before, "ComputedAt should be set by the DB NOW() default");
    }

    private static HttpResponseMessage JsonResponse(HttpStatusCode status, string json) =>
        new(status) { Content = new StringContent(json, System.Text.Encoding.UTF8, "application/json") };

    private sealed class StubHttpMessageHandler : HttpMessageHandler
    {
        private readonly Func<HttpRequestMessage, HttpResponseMessage> _responder;

        public StubHttpMessageHandler(Func<HttpRequestMessage, HttpResponseMessage> responder) => _responder = responder;

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken) =>
            Task.FromResult(_responder(request));
    }
}

/// <summary>
/// Spins up a single PostgreSQL 16 container for the whole <see cref="PersistenceTests"/> class and applies
/// the real Npgsql EF migration once. Pinned to postgres:16-alpine to match docker-compose.yml.
/// </summary>
public sealed class PostgresFixture : IAsyncLifetime
{
    private readonly PostgreSqlContainer _container = new PostgreSqlBuilder()
        .WithImage("postgres:16-alpine")
        .Build();

    public string ConnectionString => _container.GetConnectionString();

    public async Task InitializeAsync()
    {
        await _container.StartAsync();

        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseNpgsql(ConnectionString)
            .Options;
        await using var db = new AppDbContext(options);
        await db.Database.MigrateAsync();
    }

    public Task DisposeAsync() => _container.DisposeAsync().AsTask();
}

[CollectionDefinition(Name)]
public class PostgresCollection : ICollectionFixture<PostgresFixture>
{
    public const string Name = "Postgres integration";
}
