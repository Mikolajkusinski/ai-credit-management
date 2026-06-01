using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace WebApi.Migrations
{
    /// <inheritdoc />
    public partial class Init : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Clients",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    ExternalRef = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "NOW()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Clients", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Snapshots",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    ClientId = table.Column<int>(type: "integer", nullable: false),
                    SnapshotDate = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    LimitBal = table.Column<int>(type: "integer", nullable: false),
                    Sex = table.Column<int>(type: "integer", nullable: false),
                    Education = table.Column<int>(type: "integer", nullable: false),
                    Marriage = table.Column<int>(type: "integer", nullable: false),
                    Age = table.Column<int>(type: "integer", nullable: false),
                    Pay0 = table.Column<int>(type: "integer", nullable: false),
                    Pay2 = table.Column<int>(type: "integer", nullable: false),
                    Pay3 = table.Column<int>(type: "integer", nullable: false),
                    Pay4 = table.Column<int>(type: "integer", nullable: false),
                    Pay5 = table.Column<int>(type: "integer", nullable: false),
                    Pay6 = table.Column<int>(type: "integer", nullable: false),
                    BillAmt1 = table.Column<decimal>(type: "numeric", nullable: false),
                    BillAmt2 = table.Column<decimal>(type: "numeric", nullable: false),
                    BillAmt3 = table.Column<decimal>(type: "numeric", nullable: false),
                    BillAmt4 = table.Column<decimal>(type: "numeric", nullable: false),
                    BillAmt5 = table.Column<decimal>(type: "numeric", nullable: false),
                    BillAmt6 = table.Column<decimal>(type: "numeric", nullable: false),
                    PayAmt1 = table.Column<decimal>(type: "numeric", nullable: false),
                    PayAmt2 = table.Column<decimal>(type: "numeric", nullable: false),
                    PayAmt3 = table.Column<decimal>(type: "numeric", nullable: false),
                    PayAmt4 = table.Column<decimal>(type: "numeric", nullable: false),
                    PayAmt5 = table.Column<decimal>(type: "numeric", nullable: false),
                    PayAmt6 = table.Column<decimal>(type: "numeric", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Snapshots", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Snapshots_Clients_ClientId",
                        column: x => x.ClientId,
                        principalTable: "Clients",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Trends",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    ClientId = table.Column<int>(type: "integer", nullable: false),
                    ModelName = table.Column<string>(type: "character varying(32)", maxLength: 32, nullable: false),
                    Slope = table.Column<double>(type: "double precision", nullable: false),
                    Alert = table.Column<string>(type: "character varying(32)", maxLength: 32, nullable: false),
                    ComputedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "NOW()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Trends", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Trends_Clients_ClientId",
                        column: x => x.ClientId,
                        principalTable: "Clients",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Predictions",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    SnapshotId = table.Column<int>(type: "integer", nullable: false),
                    ModelName = table.Column<string>(type: "character varying(32)", maxLength: 32, nullable: false),
                    DefaultProbability = table.Column<double>(type: "double precision", nullable: false),
                    Label = table.Column<string>(type: "character varying(16)", maxLength: 16, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Predictions", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Predictions_Snapshots_SnapshotId",
                        column: x => x.SnapshotId,
                        principalTable: "Snapshots",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Clients_ExternalRef",
                table: "Clients",
                column: "ExternalRef",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Predictions_SnapshotId",
                table: "Predictions",
                column: "SnapshotId");

            migrationBuilder.CreateIndex(
                name: "IX_Snapshots_ClientId_SnapshotDate",
                table: "Snapshots",
                columns: new[] { "ClientId", "SnapshotDate" });

            migrationBuilder.CreateIndex(
                name: "IX_Trends_ClientId_ModelName",
                table: "Trends",
                columns: new[] { "ClientId", "ModelName" });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Predictions");

            migrationBuilder.DropTable(
                name: "Trends");

            migrationBuilder.DropTable(
                name: "Snapshots");

            migrationBuilder.DropTable(
                name: "Clients");
        }
    }
}
