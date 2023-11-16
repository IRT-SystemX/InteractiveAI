import * as d3 from "d3";
import graph from "./graph.json";

const config = {
  // Dimensions of the viewport
  width: 1190,
  height: 600,
  margin: { y: 24, x: 24 },
  threshold: 0,
  force: { min: 0, max: 600 }, // Max (not correlated) and min (highly correlated) distance based on their correlation coefficient
  radius: 20, // Radius of nodes in default and active state
  kpi: "nb_err", // What KPI is being looked at
  transition: 200, // Transition duration
};

export const ctx = { statuses: {} };

window.config = config;
window.ctx = ctx;

function opfabToD3(graph, kpi, linkFilterCallback = (value) => true) {
  const nodes = Object.keys(graph)
    .filter((k) => k.includes(kpi)) // Filter by KPI
    .map((k, i) => ({
      id: k.split(".")[0],
      data: Object.fromEntries(
        Object.entries(graph[k])
          .filter(([key]) => key.includes(config.kpi))
          .map(([key, value]) => [key.split(".")[0], value])
      ),
      status: [],
    }));
  let links = nodes.flatMap((node) =>
    Object.keys(node.data)
      .map((k) => ({
        source: node.id,
        target: k.split(".")[0],
        coefficient: node.data[k],
      }))
      .filter((link) => linkFilterCallback(link) && link.source !== link.target)
  );
  return {
    nodes: nodes.filter((node) =>
      links.find((value) => value.source === node.id)
    ),
    links,
  };
}

function minmax(value, max = 1, min = 0) {
  return Math.min(Math.max(min, value), max);
}

function relativeToThreshold(coefficient) {
  return minmax(
    (Math.abs(coefficient) - config.threshold) / (1 - config.threshold)
  );
}

function coeffToColor(coefficient) {
  return d3.interpolateSpectral(1 - relativeToThreshold(coefficient));
}

function setupChart() {
  const svg = d3
    .select(orange_ctx_container)
    .append("svg")
    .attr("id", "orange_chart")
    .attr("width", config.width / 4)
    .attr("height", 50);
  // Charts
  ctx.chart = svg
    .append("g")
    .attr("transform", `translate(${config.margin.x},${config.margin.y})`)
    .call(
      d3
        .axisTop(
          d3
            .scaleLinear([config.threshold, 1], d3.interpolateSpectral)
            .range([0, config.width / 4])
        )
        .ticks(8)
    );
  ctx.chart
    .append("rect")
    .attr("width", config.width / 4)
    .attr("height", 16)
    .style("fill", "url(#linear-gradient)");
  svg
    .append("defs")
    .append("linearGradient")
    .attr("id", "linear-gradient")
    .attr("x1", "0%")
    .attr("y1", "0%")
    .attr("x2", "100%")
    .attr("y2", "0%")
    .selectAll("stop")
    .data([
      { offset: "0%", color: d3.interpolateSpectral(1) },
      { offset: "25%", color: d3.interpolateSpectral(0.75) },
      { offset: "50%", color: d3.interpolateSpectral(0.5) },
      { offset: "75%", color: d3.interpolateSpectral(0.25) },
      { offset: "100%", color: d3.interpolateSpectral(0) },
    ])
    .enter()
    .append("stop")
    .attr("offset", function (d) {
      return d.offset;
    })
    .attr("stop-color", function (d) {
      return d.color;
    });
}

export function setup() {
  // Create a simulation for an array of nodes, and compose the desired forces.
  ctx.simulation = d3
    .forceSimulation()
    .force("repulsion", d3.forceCollide(config.radius * 2)) // Adds repulsion between nodes.
    .force("center", d3.forceCenter(config.width / 2, config.height / 2)); // Attracts nodes to the center of the svg area

  // Tooltip
  ctx.tooltip = d3
    .select(orange_ctx)
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

  // Main SVG
  ctx.svg = d3
    .select(orange_ctx_container)
    .append("svg")
    .attr("width", config.width)
    .attr("height", config.height)
    .attr("id", "orange_graph")
    .append("g");

  setupChart();

  // Create data
  ctx.dataset = opfabToD3(
    graph[0].data,
    config.kpi,
    (value) => Math.abs(value.coefficient) > config.threshold
  );

  console.debug(ctx.dataset);

  // Initialize the links
  ctx.links = ctx.svg
    .append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(ctx.dataset.links)
    .enter()
    .append("line")
    .attr("class", "link")
    .style("stroke", (d) => coeffToColor(d.coefficient));

  // Initialize the nodes
  ctx.nodes = ctx.svg
    .append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(ctx.dataset.nodes)
    .enter()
    .append("g")
    .attr("class", (d) => "node " + ctx.statuses[d.id]?.join(" "))
    .on("click", function (_, d) {
      if (d3.select(this).classed("focus")) {
        ctx.nodes.classed("active", false);
        ctx.nodes.classed("focus", false);
        ctx.links.classed("active", false);
        ctx.svg.classed("focus", false);
        return;
      }
      ctx.svg.classed("focus", true);
      ctx.nodes.classed("active", (node) => node.id === d.id);
      ctx.nodes.classed("focus", (node) => node.id === d.id);
      ctx.nodes.classed("active", (node) =>
        relativeToThreshold(d.data[node.id])
      );
      ctx.links.classed(
        "active",
        (link) =>
          link.source.id === d.id && relativeToThreshold(link.coefficient)
      );
    })
    .on("mouseenter", (_, d) => {
      if (ctx.svg.classed("focus")) return;

      ctx.nodes.classed("active", (node) => node.id === d.id);
      ctx.nodes.classed("hover", (node) => node.id === d.id);
      ctx.nodes.classed("active", (node) =>
        relativeToThreshold(d.data[node.id])
      );
      ctx.links.classed(
        "active",
        (link) =>
          link.source.id === d.id && relativeToThreshold(link.coefficient)
      );
    })
    .on("mouseleave", function (_, d) {
      ctx.nodes.classed("hover", false);
      if (ctx.svg.classed("focus")) return;
      ctx.nodes.classed("active", false);
      ctx.links.classed("active", false);
    })
    .on("mouseover.tooltip", function (event, d) {
      ctx.tooltip.style("opacity", 0.9);
      ctx.tooltip
        .html(
          `<b>${d.id}</b>\nCorrelations:\n${Object.keys(d.data)
            .filter((key) => d.id !== key && relativeToThreshold(d.data[key]))
            .map(
              (key) =>
                `${key}: <b style="color:${coeffToColor(
                  d.data[key]
                )};font-weight:${
                  relativeToThreshold(d.data[key]) * 1000
                }">${`${((d.data[key] / 1) * 100).toFixed(0)}%`.padStart(
                  5
                )}</b>`
            )
            .join("\n")}`
        )
        .style("left", event.pageX + config.radius + "px")
        .style("top", event.pageY + config.radius + "px");
    })
    .on("mouseout.tooltip", function () {
      ctx.tooltip.style("opacity", 0);
    })
    .on("mousemove", function (event) {
      ctx.tooltip
        .style("left", event.pageX + config.radius + "px")
        .style("top", event.pageY + config.radius + "px");
    })
    .call(
      d3
        .drag() // Sets the event listener for the specified typenames and returns the drag behavior.
        .on("start", dragstarted) // Start - after a new pointer becomes active (on mousedown or touchstart).
        .on("drag", dragged) // Drag - after an active pointer moves (on mousemove or touchmove).
        .on("end", dragended) // End - after an active pointer becomes inactive (on mouseup, touchend or touchcancel).
    );

  // Leave focus mode on click outside
  d3.select(orange_ctx_container).on("click", function (event) {
    if (ctx.svg.classed("focus") && event.target.id === "orange_graph") {
      ctx.nodes.classed("active", false);
      ctx.nodes.classed("focus", false);
      ctx.nodes.classed("hover", false);
      ctx.links.classed("active", false);
      ctx.svg.classed("focus", false);
    }
  });

  ctx.nodes.append("circle").attr("r", (d) => config.radius);
  ctx.nodes
    .append("text")
    .attr("class", "label")
    .attr("dy", ".3em")
    .text((d) => d.id);

  // Listen for tick events to render the nodes as they update in your Canvas or SVG.
  ctx.simulation
    .nodes(ctx.dataset.nodes) // Sets the simulation’s nodes to the specified array of objects, initializing their positions and velocities, and then re-initializes any bound forces;
    .on("tick", ticked); // Use simulation.on to listen for tick events as the simulation runs.
  // After this, Each node must be an object. The following properties are assigned by the simulation:
  // index - the node’s zero-based index into nodes
  // x - the node’s current x-position
  // y - the node’s current y-position
  // vx - the node’s current x-velocity
  // vy - the node’s current y-velocity

  ctx.simulation.force(
    "link",
    d3
      .forceLink() // This force provides links between nodes
      .links(ctx.dataset.links)
      .distance(
        (link) =>
          config.force.max -
          ((config.force.max - config.force.min) *
            Math.log(relativeToThreshold(link.coefficient) + 1)) /
            Math.log(2)
      )
      .id((d) => d.id) // This sets the node id accessor to the specified function. If not specified, will default to the index of a node.
  );

  // This function is run at each iteration of the force algorithm, updating the nodes position (the nodes data array is directly manipulated).
  function ticked() {
    ctx.links
      .attr("x1", (d) =>
        minmax(d.source.x, config.width - config.margin.x, config.margin.x)
      )
      .attr("y1", (d) =>
        minmax(d.source.y, config.height - config.margin.y, config.margin.y)
      )
      .attr("x2", (d) =>
        minmax(d.target.x, config.width - config.margin.x, config.margin.x)
      )
      .attr("y2", (d) =>
        minmax(d.target.y, config.height - config.margin.y, config.margin.y)
      );

    ctx.nodes.attr(
      "transform",
      (d) =>
        `translate(${minmax(
          d.x,
          config.width - config.margin.x,
          config.margin.x
        )},${minmax(d.y, config.height - config.margin.y, config.margin.y)})`
    );
  }

  // Create zoom handler
  const zoom_handler = d3
    .zoom()
    .scaleExtent([1, Infinity])
    .translateExtent([
      [0, 0],
      [config.width, config.height],
    ])
    .on("zoom", zoom_actions);

  // Specify what to do when zoom event listener is triggered
  function zoom_actions(event) {
    ctx.svg.attr("transform", event.transform);
  }

  // Add zoom behaviour to the svg element
  // Same as svg.call(zoom_handler);
  zoom_handler(d3.select(orange_ctx_container));

  // When the drag gesture starts, the targeted node is fixed to the pointer
  // The simulation is temporarily “heated” during interaction by setting the target alpha to a non-zero value.
  function dragstarted(event, d) {
    if (!event.active) ctx.simulation.alphaTarget(0.3).restart(); // Sets the current target alpha to the specified number in the range [0,1].
    d.fy = d.y; // Fx - the node’s fixed x-position. Original is null.
    d.fx = d.x; // Fy - the node’s fixed y-position. Original is null.
  }

  // When the drag gesture starts, the targeted node is fixed to the pointer
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  // The targeted node is released when the gesture ends
  function dragended(event, d) {
    if (!event.active) ctx.simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}

export function setThreshold(value) {
  config.threshold = value;
  orange_ctx_container.innerHTML = "";
  setup();
}

export function setStatus(node, severity) {
  if (ctx.statuses[node]) ctx.statuses[node].push(severity);
  else ctx.statuses[node] = [severity];
  if (ctx.nodes) ctx.nodes.filter((d) => d.id === node).classed(severity, true);
}
