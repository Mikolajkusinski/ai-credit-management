using WebApi.Models;

namespace WebApi.Tests;

public class SmokeTests
{
    [Fact]
    public void PredictRequest_CanBeInstantiated_FromTestProject()
    {
        var request = new PredictRequest();

        Assert.Equal(0, request.LimitBal);
        Assert.Equal(0, request.Age);
    }
}
