import * as d3 from "d3";
import graph from "./graph.json";

const config = {
  width: 1190,
  height: 600,
  margin: { y: 30, x: 50 },
  distance: 800,
  strength: -800,
  radius: { default: 20, hover: 30 },
  kpi: "composite.ratio_pl",
  transition: 200,
};

function opfabToD3(graph, attr, linkFilterCallback = (value) => true) {
  const nodes = Object.keys(graph)
    .filter((k) => k.includes(attr))
    .map((k, i) => ({
      id: k,
      data: Object.keys(graph[k])
        .filter((l) => l.includes(attr) && graph[k][l])
        .map((l) => ({ [l]: graph[k][l] })),
    }));
  let links = [];
  for (const node of nodes) {
    links = [
      ...links,
      ...node.data
        .map((k) => ({
          source: node.id,
          target: Object.keys(k)[0],
          force: Object.values(k)[0],
        }))
        .filter((value, index) => linkFilterCallback(value, index)),
    ];
  }
  return { nodes, links };
}

function minmax(value, max, min = 0) {
  return Math.min(Math.max(min, value), max);
}

export function setup() {
  //create a simulation for an array of nodes, and compose the desired forces.
  let simulation = d3
    .forceSimulation()
    .force(
      "link",
      d3
        .forceLink() // This force provides links between nodes
        .id((d) => d.id) // This sets the node id accessor to the specified function. If not specified, will default to the index of a node.
    )
    .force("charge", d3.forceManyBody().strength(config.strength)) // This adds repulsion (if it's negative) between nodes.
    .force("center", d3.forceCenter(config.width / 2, config.height / 2)); // This force attracts nodes to the center of the svg area

  var tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

  const svg = d3
    .select(orange_ctx_container)
    .append("svg")
    .attr("width", config.width)
    .attr("height", config.height)
    .append("g");

  //create dummy data
  const dataset = opfabToD3(graph[0].data, config.kpi, (v) => v.force > 0.3);

  // Initialize the links
  const link = svg
    .append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(dataset.links)
    .enter()
    .append("line")
    .style("stroke", (d) =>
      d.force > 0 ? d3.interpolateReds(d.force) : d3.interpolateBlues(-d.force)
    );

  // Initialize the nodes
  // add hover over effect
  const node = svg
    .append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(dataset.nodes)
    .enter()
    .append("g")
    .attr("transform", (d) => `translate(${d.x},${d.y})`)
    .on("mouseover", function (d) {
      d3.select(this)
        .select("circle")
        .transition()
        .duration(config.transition)
        .attr("r", config.radius.hover)
        .style("fill", "#a00");
    })
    .on("mouseout", function (d) {
      d3.select(this)
        .select("circle")
        .transition()
        .duration(config.transition)
        .attr("r", config.radius.default)
        .style("fill", "#000");
    })
    .on("mouseover.tooltip", function (event, d) {
      tooltip.transition().duration(config.transition).style("opacity", 0.8);
      tooltip
        .text(
          `ID: ${d.id.split(".")[0]}\nLinks:\n${d.data
            .map(
              (value) =>
                `${Object.keys(value)[0].split(".")[0]}: ${Object.values(
                  value
                )[0].toFixed(5)}`
            )
            .join("\n")}`
        )
        .style("left", event.pageX + "px")
        .style("top", event.pageY + 10 + "px");
    })
    .on("mouseout.tooltip", function () {
      tooltip.transition().duration(config.transition).style("opacity", 0);
    })
    .on("mousemove", function (event) {
      tooltip
        .style("left", event.pageX + "px")
        .style("top", event.pageY + 10 + "px");
    })
    .call(
      d3
        .drag() //sets the event listener for the specified typenames and returns the drag behavior.
        .on("start", dragstarted) //start - after a new pointer becomes active (on mousedown or touchstart).
        .on("drag", dragged) //drag - after an active pointer moves (on mousemove or touchmove).
        .on("end", dragended) //end - after an active pointer becomes inactive (on mouseup, touchend or touchcancel).
    );

  node.append("circle").attr("r", (d) => config.radius.default);
  //  text-anchor="middle" fill="white" font-size="10px" font-family="Arial" dy=".3em"
  node
    .append("text")
    .attr("class", "label")
    .attr("dy", ".3em")
    .text((d) => d.id.split(".")[0]);

  //Listen for tick events to render the nodes as they update in your Canvas or SVG.
  simulation
    .nodes(dataset.nodes) //sets the simulation’s nodes to the specified array of objects, initializing their positions and velocities, and then re-initializes any bound forces;
    .on("tick", ticked); //use simulation.on to listen for tick events as the simulation runs.
  // After this, Each node must be an object. The following properties are assigned by the simulation:
  // index - the node’s zero-based index into nodes
  // x - the node’s current x-position
  // y - the node’s current y-position
  // vx - the node’s current x-velocity
  // vy - the node’s current y-velocity

  simulation.force("link").links(dataset.links).distance(distance);

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
  //create zoom handler
  var zoom_handler = d3.zoom().on("zoom", zoom_actions);

  //specify what to do when zoom event listener is triggered
  function zoom_actions(event) {
    svg.attr("transform", event.transform);
  }

  //add zoom behaviour to the svg element
  //same as svg.call(zoom_handler);
  zoom_handler(svg);

  //When the drag gesture starts, the targeted node is fixed to the pointer
  //The simulation is temporarily “heated” during interaction by setting the target alpha to a non-zero value.
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart(); //sets the current target alpha to the specified number in the range [0,1].
    d.fy = d.y; //fx - the node’s fixed x-position. Original is null.
    d.fx = d.x; //fy - the node’s fixed y-position. Original is null.
  }

  //When the drag gesture starts, the targeted node is fixed to the pointer
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  //the targeted node is released when the gesture ends
  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;

    //console.log("dataset after dragged is ...",dataset);
  }
}
