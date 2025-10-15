// EXTERNAL:colors.js
// Utility function to convert hex color to an RGB object
function hexToRgb(hex) {
    const bigint = parseInt(hex.slice(1), 16);
    return {
        r: (bigint >> 16) & 255,
        g: (bigint >> 8) & 255,
        b: bigint & 255
    };
}

// Function to get interpolated color by passing a value from 0 to 1
function getColor(value, cmin, cmax, colorMap) {
    let colors;

    // Define color scales based on the selected colormap
    if (colorMap === 'BrBG') {
        colors = [
            "#543005",
            "#8C510A", "#BF812D", "#DFC27D", "#F6E8C3",
            "#F5F5F5", "#C7EAE5", "#80CDC1", "#35978F", "#01665E",
            "#003C30"
        ];
    } else if (colorMap === 'balance') {
        colors = [
            "#2a0a0a",
            "#751b1b", "#b73c3c", "#e88484", "#f3c3c3", // Negative side
            "#ffffff",                                            // Neutral middle
            "#c3e4f3", "#84c2e8", "#3c9fb7", "#1b5e75",  // Positive side
            "#0a2a2a"
        ];
        colors = colors.reverse()
    } else if (colorMap === 'RdBu') {
        colors = ['#ff0000', '#ffffff', '#0000ff'];
    } else if (colorMap === 'BuRd') {
        colors = ['#0000ff', '#ffffff', '#ff0000'];
    } else {
        throw new Error("Invalid colorMap. Choose 'BrBG', 'balance', 'BuRd', or 'RdBu'.");
    }

    let x;
    if (value > 0) {
        x = 0.5 + (value / cmax) * 0.5;  // Map positive values from 0.5 to 1.0
    } else if (value < 0) {
        x = 0.5 + (value / (-cmin)) * 0.5;  // Map negative values from 0.0 to 0.5
    } else {
        x = 0.5;  // Zero maps to middle
    }    

    // Clamp value between 0 and 1
    x = Math.min(1, Math.max(0, x));
    if (isNaN(x)) {
        return `rgba(255, 255, 255, 0.5)`;
    }

    // Compute exact position in color array
    const scaledValue = x * (colors.length - 1);
    const lowerIndex = Math.floor(scaledValue);
    const upperIndex = Math.ceil(scaledValue);

    // Edge case: if at the end of the array, return the last color
    if (lowerIndex === upperIndex) {
        const color = hexToRgb(colors[lowerIndex]);
        return `rgba(${color.r}, ${color.g}, ${color.b}, 0.5)`;
    }

    // Interpolate between the two colors
    const lowerColor = hexToRgb(colors[lowerIndex]);
    const upperColor = hexToRgb(colors[upperIndex]);
    const t = scaledValue - lowerIndex;

    // Interpolate RGB channels
    const r = Math.round(lowerColor.r + t * (upperColor.r - lowerColor.r));
    const g = Math.round(lowerColor.g + t * (upperColor.g - lowerColor.g));
    const b = Math.round(lowerColor.b + t * (upperColor.b - lowerColor.b));

    // Return the interpolated color as an rgb(r, g, b) string
    return `rgba(${r}, ${g}, ${b}, 0.5)`;
}