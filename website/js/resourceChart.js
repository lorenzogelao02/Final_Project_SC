const fallbackResourceData = [
  { Borough: "Manhattan", Fountains: 909, Toilets: 2, Centers: 3, LinkNYC: 1231 },
  { Borough: "Brooklyn", Fountains: 1118, Toilets: 3, Centers: 1, LinkNYC: 357 },
  { Borough: "Bronx", Fountains: 590, Toilets: 1, Centers: 1, LinkNYC: 216 },
  { Borough: "Queens", Fountains: 978, Toilets: 1, Centers: 2, LinkNYC: 401 },
  { Borough: "Staten Island", Fountains: 254, Toilets: 0, Centers: 1, LinkNYC: 50 }
];

async function loadResourceChart() {
  const chartDiv = document.getElementById("resourceChart");
  if (!chartDiv || typeof Plotly === "undefined") return;

  const data = fallbackResourceData;
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
