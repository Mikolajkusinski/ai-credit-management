using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using WebApi.Data;
using WebApi.Models;
using WebApi.Services;

namespace WebApi.Tests;

/// <summary>
/// Integration tests for GET /api/v1/monitoring/clients (CREDIT-302 enabler). Clients are seeded via
/// the POST snapshots endpoint (CREDIT-203), so this exercises the write→list loop. Same harness as
/// ClientHistoryTests: Flask is stubbed and the DbContext is swapped to the EF Core in-memory provider.
/// </summary>
public class ClientListTests
{
    // Contract-shaped Flask response: W3 = 0.58/0.61/0.55, increasing trends for every model.
    private const string FlaskHappyBody = """
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

    private static WebApplicationFactory<Program> CreateFactory(string dbName)
    {
        return new WebApplicationFactory<Program>().WithWebHostBuilder(builder =>
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureTestServices(services =>
            {
                services.AddHttpClient<PythonModelClient>()
                    .ConfigurePrimaryHttpMessageHandler(() => new StubHttpMessageHandler(
                        _ => JsonResponse(HttpStatusCode.OK, FlaskHappyBody)));

                services.RemoveAll(typeof(DbContextOptions<AppDbContext>));
                services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase(dbName));
            });
        });
    }

    private static object ValidFeatures() => new
    {
        limitBal = 100000,
        sex = 1,
        education = 2,
        marriage = 1,
        age = 35,
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
    public async Task GetClients_NoData_Returns200_EmptyList()
    {
        await using var factory = CreateFactory(Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        var response = await client.GetAsync("/api/v1/monitoring/clients");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var body = await response.Content.ReadFromJsonAsync<ClientListResponse>();
        Assert.NotNull(body);
        Assert.Empty(body!.Clients);
    }

    [Fact]
    public async Task GetClients_AfterSnapshots_ListsClientsWithStats_NewestActivityFirst()
    {
        await using var factory = CreateFactory(Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        // alpha: two snapshots, latest 2026-05-24. beta: one snapshot, latest 2026-04-15 (older).
        await PostSnapshot(client, "alpha", "2026-05-10");
        await PostSnapshot(client, "alpha", "2026-05-24");
        await PostSnapshot(client, "beta", "2026-04-15");

        var response = await client.GetAsync("/api/v1/monitoring/clients");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var body = await response.Content.ReadFromJsonAsync<ClientListResponse>();
        Assert.NotNull(body);
        Assert.Equal(2, body!.Clients.Count);

        // Ordered by most-recent snapshot first → alpha before beta.
        var alpha = body.Clients[0];
        Assert.Equal("alpha", alpha.ClientRef);
        Assert.Equal(2, alpha.SnapshotCount);
        Assert.Equal(new DateOnly(2026, 5, 24), alpha.LatestSnapshotDate);
        Assert.Equal("INCREASING_RISK", alpha.LatestAlert);

        var beta = body.Clients[1];
        Assert.Equal("beta", beta.ClientRef);
        Assert.Equal(1, beta.SnapshotCount);
        Assert.Equal(new DateOnly(2026, 4, 15), beta.LatestSnapshotDate);
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
