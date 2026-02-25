// EXTERNAL:time_grouping_utilities.js

const MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
];

const MONTH_CODE_TO_NAME = MONTH_NAMES.reduce((acc, name, idx) => {
    const monthNum = idx + 1;
    acc[`M${String(monthNum).padStart(2, "0")}`] = name;
    return acc;
}, {});

const MONTH_NAME_TO_NUMBER = MONTH_NAMES.reduce((acc, name, idx) => {
    acc[name.toLowerCase()] = idx + 1;
    return acc;
}, {});

function parseMonthToken(rawValue) {
    const value = String(rawValue || "").trim();
    if (!value) {
        return null;
    }

    const monthCodeMatch = value.match(/^M(0?[1-9]|1[0-2])$/i);
    if (monthCodeMatch) {
        return Number(monthCodeMatch[1]);
    }

    const monthNumberMatch = value.match(/^(0?[1-9]|1[0-2])$/);
    if (monthNumberMatch) {
        return Number(monthNumberMatch[1]);
    }

    return MONTH_NAME_TO_NUMBER[value.toLowerCase()] || null;
}

function formatMonthToken(monthNumber, outputMode = "MXX") {
    if (!Number.isFinite(monthNumber) || monthNumber < 1 || monthNumber > 12) {
        return "";
    }
    if (outputMode === "NUMBER") {
        return String(monthNumber);
    }
    return `M${String(monthNumber).padStart(2, "0")}`;
}

function normalizeTimeFilter(raw, outputMode = "MXX") {
    if (!raw || raw === "None") {
        return raw;
    }

    return String(raw)
        .split(",")
        .map((part) => {
            const trimmed = part.trim();
            const monthNumber = parseMonthToken(trimmed);
            if (!monthNumber) {
                return trimmed;
            }
            return formatMonthToken(monthNumber, outputMode);
        })
        .join(",");
}

function humanizeTimeFilter(raw) {
    if (!raw || raw === "None") return raw;

    return String(raw)
        .split(",")
        .map((part) => {
            const monthNumber = parseMonthToken(part);
            if (!monthNumber) {
                return String(part).trim();
            }
            return MONTH_NAMES[monthNumber - 1];
        })
        .join(", ");
}
