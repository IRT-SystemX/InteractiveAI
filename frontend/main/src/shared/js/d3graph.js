import * as d3 from "d3";
import graph from "./graph.json";

const config = {
  // Dimensions of the viewport
  width: 1190,
  height: 600,
  margin: { y: 30, x: 50 },
  threshold: 0.1,
  distance: 500, // Max distance between two linked nodes
  force: { min: 0, max: 500 }, // Max (not correlated) and min (highly correlated) distance based on their correlation coefficient
  radius: { default: 20, active: 30 }, // Radius of nodes in default and active state
  kpi: "nb_err", // What KPI is being looked at
  transition: 200, // Transition duration
};

function opfabToD3(graph, kpi, linkFilterCallback = (value) => true) {
  const nodes = Object.keys(graph)
    .filter((k) => k.includes(kpi)) // Filter by KPI
    .map((k, i) => ({
      id: k,
      data: Object.fromEntries(
        Object.entries(graph[k]).filter(([key]) => key.includes(config.kpi))
      ),
    }));
  let links = [];
  for (const node of nodes) {
    links = [
      ...links,
      ...Object.keys(node.data)
        .map((k) => ({
          source: node.id,
          target: k,
          coefficient: node.data[k],
        }))
        .filter((value, index) => linkFilterCallback(value, index)),
    ];
  }
  return { nodes, links };
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

export function setup() {
  // Create a simulation for an array of nodes, and compose the desired forces.
  let simulation = d3
    .forceSimulation()
    .force("repulsion", d3.forceCollide(config.radius.active)) // This adds repulsion (if it's negative) between nodes.
    .force("center", d3.forceCenter(config.width / 2, config.height / 2)); // This force attracts nodes to the center of the svg area

  // Tooltip
  var tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

  // Main SVG
  const svg = d3
    .select(orange_ctx_container)
    .append("svg")
    .attr("width", config.width)
    .attr("height", config.height)
    .append("g");

  // Create data
  const dataset = opfabToD3(
    graph[0].data,
    config.kpi,
    (value) => Math.abs(value.coefficient) > config.threshold
  );

  console.debug(dataset);

  // Initialize the links
  const link = svg
    .append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(dataset.links)
    .enter()
    .append("line")
    .style("stroke", (d) => coeffToColor(d.coefficient));

  // Initialize the nodes
  const node = svg
    .append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(dataset.nodes)
    .enter()
    .append("g")
    .on("click", (_, d) => {
      node.style("opacity", 1);
      link.style("opacity", 1);
      node
        .filter((node) => !relativeToThreshold(d.data[node.id]))
        .style("opacity", 0);
      link
        .filter(
          (node) =>
            !(node.source.id === d.id && relativeToThreshold(node.coefficient))
        )
        .style("opacity", 0);
    })
    // Hover effect
    .on("mouseover", function (d) {
      d3.select(this).select("circle").transition().style("stroke-width", "10");
    })
    .on("mouseout", function (d) {
      d3.select(this)
        .select("circle")
        .transition()
        .attr("r", config.radius.default)
        .style("stroke-width", "0");
    })
    .on("mouseover.tooltip", function (event, d) {
      tooltip.transition().style("opacity", 0.8);
      tooltip
        .html(
          `<b>${d.id.split(".")[0]}</b>\nCorrelations:\n${Object.keys(d.data)
            .filter((key) => d.id !== key)
            .map(
              (key) =>
                `${key.split(".")[0]}: <b style="color:${coeffToColor(
                  d.data[key]
                )};font-weight:${
                  relativeToThreshold(d.data[key]) * 1000
                }">${`${((d.data[key] / 1) * 100).toFixed(0)}%`.padStart(
                  5
                )}</b>`
            )
            .join("\n")}`
        )
        .style("left", event.pageX + "px")
        .style("top", event.pageY + 10 + "px");
    })
    .on("mouseout.tooltip", function () {
      tooltip.transition().style("opacity", 0);
    })
    .on("mousemove", function (event) {
      tooltip
        .style("left", event.pageX + "px")
        .style("top", event.pageY + 10 + "px");
    })
    .call(
      d3
        .drag() // Sets the event listener for the specified typenames and returns the drag behavior.
        .on("start", dragstarted) // Start - after a new pointer becomes active (on mousedown or touchstart).
        .on("drag", dragged) // Drag - after an active pointer moves (on mousemove or touchmove).
        .on("end", dragended) // End - after an active pointer becomes inactive (on mouseup, touchend or touchcancel).
    );

  node.append("circle").attr("r", (d) => config.radius.default);
  //  text-anchor="middle" fill="white" font-size="10px" font-family="Arial" dy=".3em"
  node
    .append("text")
    .attr("class", "label")
    .attr("dy", ".3em")
    .text((d) => d.id.split(".")[0]);

  // Listen for tick events to render the nodes as they update in your Canvas or SVG.
  simulation
    .nodes(dataset.nodes) // Sets the simulation’s nodes to the specified array of objects, initializing their positions and velocities, and then re-initializes any bound forces;
    .on("tick", ticked); // Use simulation.on to listen for tick events as the simulation runs.
  // After this, Each node must be an object. The following properties are assigned by the simulation:
  // index - the node’s zero-based index into nodes
  // x - the node’s current x-position
  // y - the node’s current y-position
  // vx - the node’s current x-velocity
  // vy - the node’s current y-velocity

  simulation.force(
    "link",
    d3
      .forceLink() // This force provides links between nodes

      .links(dataset.links)
      .distance(
        (link) =>
          config.force.max -
          (config.force.max - config.force.min) *
            relativeToThreshold(link.coefficient)
      )
      .id((d) => d.id) // This sets the node id accessor to the specified function. If not specified, will default to the index of a node.
  );

  // This function is run at each iteration of the force algorithm, updating the nodes position (the nodes data array is directly manipulated).
  function ticked() {
    link
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

    node.attr(
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
  var zoom_handler = d3.zoom().on("zoom", zoom_actions);

  // Specify what to do when zoom event listener is triggered
  function zoom_actions(event) {
    svg.attr("transform", event.transform);
  }

  // Add zoom behaviour to the svg element
  // Same as svg.call(zoom_handler);
  zoom_handler(svg);

  // When the drag gesture starts, the targeted node is fixed to the pointer
  // The simulation is temporarily “heated” during interaction by setting the target alpha to a non-zero value.
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart(); // Sets the current target alpha to the specified number in the range [0,1].
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
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}
