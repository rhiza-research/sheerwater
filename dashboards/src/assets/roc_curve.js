// EXTERNAL:roc_curve.js

let series = data.series[0];

// --- Safe read dashboard variables ---
function getVar(name, defaultValue) {
    return (variables && variables[name] && variables[name].current)
        ? variables[name].current.value
        : defaultValue;
}

let station = String(getVar("station")).trim();     
let satellite = String(getVar("satellite")).trim(); 
let selectedMonths = getVar("months", ["$__all"]); // multi-select months

// --- Build field names ---
let truthFieldName = `${station}_precip`;     
let climatologyFieldName = `climatology_tahmo_avg_2015_2025_precip`;
let predFieldName  = `${satellite}_precip`;   

// --- Find fields ---
let truthField = series.fields.find(f => f.name === truthFieldName);
let climatologyField = series.fields.find(f => f.name === climatologyFieldName);
let predField  = series.fields.find(f => f.name === predFieldName);
let timeField  = series.fields.find(f => f.name === "time");

if (!truthField || !predField || !climatologyField || !timeField) {
    throw new Error("Required fields (truth, prediction, climatology, time) not found.");
}

// --- Extract arrays ---
let truthValuesAll = Array.from(truthField.values || truthField.values.buffer || []);
let climatologyValuesAll = Array.from(climatologyField.values || climatologyField.values.buffer || []);
let predValuesAll  = Array.from(predField.values  || predField.values.buffer  || []);
let timeAll        = Array.from(timeField.values || timeField.values.buffer || []);

// --- Filter by selected months ---
let useAll = Array.isArray(selectedMonths) && selectedMonths.includes("$__all");
let selectedMonthNumbers = selectedMonths.map(m => parseInt(m.replace(/^M/, ""), 10)); // M01 -> 1

let filteredIndexes = timeAll.map((t,i) => {
    if (useAll) return i;
    let month = new Date(t).getMonth() + 1;
    return selectedMonthNumbers.includes(month) ? i : -1;
}).filter(i => i >= 0);

if (filteredIndexes.length === 0) throw new Error("No points match the selected months.");

// --- Filter arrays ---
let truthValues = filteredIndexes.map(i => truthValuesAll[i] - climatologyValuesAll[i]); // subtract climatology
let predValues  = filteredIndexes.map(i => predValuesAll[i]);
let timeValues  = filteredIndexes.map(i => timeAll[i]);

// --- Build classification arrays using event threshold = 0 ---
let yTrue = [];
let yScore = [];

for (let i = 0; i < truthValues.length; i++) {
    let t = truthValues[i];
    let p = predValues[i];
    if (typeof t === "number" && typeof p === "number" && !isNaN(t) && !isNaN(p)) {
        yTrue.push(t >= 0 ? 1 : 0);
        yScore.push(p);
    }
}

// --- Count totals ---
let totalWet = yTrue.filter(v => v === 1).length;
let totalDry = yTrue.filter(v => v === 0).length;

if (totalWet === 0 || totalDry === 0) {
    throw new Error("Need both wet and dry cases to compute ROC.");
}

// --- Sweep satellite thresholds ---
let minP = Math.min(...yScore);
let maxP = Math.max(...yScore);
let steps = 100;

let thresholds = [];
for (let i = 0; i <= steps; i++) thresholds.push(maxP - i * (maxP - minP) / steps);

let TPR = [];
let FPR = [];
let youden = [];

thresholds.forEach(thresh => {
    let TP=0, FP=0;
    for (let i=0; i<yScore.length; i++) {
        if (yScore[i] >= thresh) {
            if (yTrue[i] === 1) TP++; else FP++;
        }
    }
    TPR.push(TP/totalWet);
    FPR.push(FP/totalDry);
    youden.push(TP/totalWet - FP/totalDry);
});

// Ensure endpoints
TPR.unshift(0); FPR.unshift(0);
TPR.push(1); FPR.push(1);

// --- Compute AUC ---
let auc = 0;
for (let i=1; i<FPR.length; i++) {
    let width = FPR[i]-FPR[i-1];
    let height = (TPR[i]+TPR[i-1])/2;
    auc += width*height;
}

// --- Find optimal threshold ---
let bestIndex = youden.indexOf(Math.max(...youden));
let bestThreshold = thresholds[bestIndex];
let bestTPR = TPR[bestIndex+1];
let bestFPR = FPR[bestIndex+1];

// --- Plot ---
return {
    data: [
        { x:FPR, y:TPR, type:'scatter', mode:'lines', line:{width:3}, name:`ROC (AUC = ${auc.toFixed(3)})` },
        { x:[0,1], y:[0,1], type:'scatter', mode:'lines', line:{dash:'dash', color:'gray'}, name:'Random' },
        { x:[bestFPR], y:[bestTPR], type:'scatter', mode:'markers', marker:{size:10,color:'red'}, name:`Optimal Threshold = ${bestThreshold.toFixed(2)}` }
    ],
    layout: {
        xaxis: { title: "False Positive Rate", type:"linear", range:[0,1], autorange:false },
        yaxis: { title: "True Positive Rate", type:"linear", range:[0,1], autorange:false },
        showlegend: true
    }
};
