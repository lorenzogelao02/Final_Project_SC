const fallbackResourceData = [
  { Borough: "Manhattan", Fountains: 909, Toilets: 2, Centers: 3, LinkNYC: 1231 },
  { Borough: "Brooklyn", Fountains: 1118, Toilets: 3, Centers: 1, LinkNYC: 357 },
  { Borough: "Bronx", Fountains: 590, Toilets: 1, Centers: 1, LinkNYC: 216 },
  { Borough: "Queens", Fountains: 978, Toilets: 1, Centers: 2, LinkNYC: 401 },
  { Borough: "Staten Island", Fountains: 254, Toilets: 0, Centers: 1, LinkNYC: 50 }
];

function parseCSV(text) {
  const lines = text.trim().split("\n");
  const headers = lines[0].split(",").map(h => h.trim());

  return lines.slice(1).map(line => {
    const values = line.split(",").map(v => v.trim());
    const row = {};

    headers.forEach((header, index) => {
      row[header || "Borough"] = values[index];
    });

    return row;
  });
}

async function getResourceData() {
  try {
    const response = await fetch("assets/data/resource_summary.csv");

    if (!response.ok) {
      throw new Error("CSV file not found");
    }

    const text = await response.text();
    const rows = parseCSV(text);

    return rows.map(row => ({
      Borough: row.Borough || row.borough || row.index || row[""] || "",
      Fountains: Number(row.Fountains || 0),
      Toilets: Number(row.Toilets || 0),
      Centers: Number(row.Centers || 0),
      LinkNYC: Number(row.LinkNYC || 0)
    }));
  } catch (error) {
    console.warn("Using fallback chart data because resource_summary.csv could not be loaded.");
    return fallbackResourceData;
  }
}

async function loadResourceChart() {
  const chartDiv = document.getElementById("resourceChart");
  if (!chartDiv || typeof Plotly === "undefined") return;

  const data = await getResourceData();
  const boroughs = data.map(d => d.Borough);

  const resources = ["Fountains", "Toilets", "Centers", "LinkNYC"];

  const traces = resources.map(resource => ({
    x: boroughs,
    y: data.map(d => Math.max(Number(d[resource]), 0.1)),
    text: data.map(d => String(Number(d[resource]))),
    name: resource,
    type: "bar",
    hovertemplate: `<b>%{x}</b><br>${resource}: %{text}<extra></extra>`
  }));

  const layout = {
    barmode: "group",
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: {
      color: "#f4f7fb",
      family: "Inter, sans-serif"
    },
    yaxis: {
      title: "Count, log scale",
      type: "log",
      gridcolor: "rgba(255,255,255,0.12)",
      zerolinecolor: "rgba(255,255,255,0.12)"
    },
    xaxis: {
      title: "Borough",
      gridcolor: "rgba(255,255,255,0.08)"
    },
    legend: {
      orientation: "h",
      y: -0.25
    },
    margin: {
      t: 30,
      r: 20,
      b: 90,
      l: 70
    }
  };

  const config = {
    responsive: true,
    displayModeBar: true
  };

  Plotly.newPlot("resourceChart", traces, layout, config);
}

document.addEventListener("DOMContentLoaded", loadResourceChart);
