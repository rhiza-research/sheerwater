const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function loadTerracottaUtilities(overrides = {}) {
    const filePath = path.resolve(
        __dirname,
        "../src/assets/terracotta_dataset_utilities.js"
    );
    const source = fs.readFileSync(filePath, "utf8");
    const context = {
        console,
        resolveRegion: (forecast) =>
            forecast === "salient" ? "africa" : "global",
        resolveSkillScoreSpec: () => ({
            supported: true,
            computeMode: "skill_score",
            expression: "(1-v1/v2)",
            range: { min: -1, max: 1 },
            displayRange: { min: -1, max: 1 },
            colormap: "rdylgn",
        }),
        ...overrides,
    };
    vm.createContext(context);
    vm.runInContext(source, context, { filename: filePath });
    return context;
}

function groupedMetricParams(overrides = {}) {
    return {
        forecast: "ecmwf_ifs_er",
        forecast_ref: "None",
        referenceVarMap: { forecast: "forecast_ref" },
        grid: "1_5",
        metric: "acc",
        product: "era5_precip",
        lead: "week1",
        timeGrouping: "None",
        timeFilter: "None",
        timeFilterOutputMode: "NUMBER",
        region: "global",
        ...overrides,
    };
}

function loadMultimapParams() {
    const filePath = path.resolve(
        __dirname,
        "../src/assets/bfd145p7u3jlse-multimap-forecast-evaluation-params.js"
    );
    const source = fs.readFileSync(filePath, "utf8");
    const context = {
        readVar: (_name, fallback = "") => fallback,
    };
    vm.createContext(context);
    vm.runInContext(source, context, { filename: filePath });
    return context;
}

test("resolveRegion defaults to global when there is no forecast-specific override", () => {
    const { resolveRegion } = loadMultimapParams();

    assert.equal(resolveRegion("ecmwf_ifs_er"), "global");
    assert.equal(resolveRegion(undefined), "global");
    assert.equal(resolveRegion("salient"), "africa");
});

test("compute mode defaults to global when both forecasts support it", () => {
    const { resolveTerracottaTileRequest } = loadTerracottaUtilities();

    const request = resolveTerracottaTileRequest(
        groupedMetricParams({ forecast_ref: "fuxi" })
    );

    assert.equal(request.computeMode, "skill_score");
    assert.match(request.datasetId, /_global_True_/);
    assert.match(request.computeDatasetId2, /_global_True_/);
});

test("shared region uses the reference forecast region when primary is global", () => {
    const { resolveTerracottaTileRequest } = loadTerracottaUtilities();

    const request = resolveTerracottaTileRequest(
        groupedMetricParams({ forecast_ref: "salient" })
    );

    assert.equal(request.computeMode, "skill_score");
    assert.match(request.datasetId, /_africa_True_/);
    assert.match(request.computeDatasetId2, /_africa_True_/);
});

test("shared region uses the primary forecast region when reference is global", () => {
    const { resolveTerracottaTileRequest } = loadTerracottaUtilities();

    const request = resolveTerracottaTileRequest(
        groupedMetricParams({
            forecast: "salient",
            forecast_ref: "ecmwf_ifs_er",
            region: "africa",
        })
    );

    assert.equal(request.computeMode, "skill_score");
    assert.match(request.datasetId, /_africa_True_/);
    assert.match(request.computeDatasetId2, /_africa_True_/);
});

test("shared region prefers the primary region when both forecasts are non-global", () => {
    const { resolveTerracottaTileRequest } = loadTerracottaUtilities({
        resolveRegion: (forecast) => {
            if (forecast === "salient") return "africa";
            if (forecast === "custom_primary") return "europe";
            return "global";
        },
    });

    const request = resolveTerracottaTileRequest(
        groupedMetricParams({
            forecast: "custom_primary",
            forecast_ref: "salient",
            region: "europe",
        })
    );

    assert.equal(request.computeMode, "skill_score");
    assert.match(request.datasetId, /_europe_True_/);
    assert.match(request.computeDatasetId2, /_europe_True_/);
});
