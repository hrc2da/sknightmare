class TrackingGraph {
  constructor(svg, x, y, w, h, attribute, id, name = undefined) {
    this.svg = svg;
    this.attribute = attribute;
    if (name) {
      this.name = name;
    } else {
      this.name = attribute;
    }
    this.num_days = 0;
    this.max_val = 1.0;
    this.min_val = 0.0;
    this.padding = 45;
    this.x = x;
    this.id = id;
    this.width = w;
    this.y = y;
    this.height = h;
    this.make_x_scale = () => {
      return d3
        .scaleLinear()
        .domain([0, this.num_days])
        .range([this.x + this.padding, this.x + this.width]);
    };
    this.make_y_scale = () => {
      return d3
        .scaleLinear()
        .domain([this.max_val, this.min_val])
        .range([this.y + this.padding, this.y + this.height]);
    };
    this.data = [];
    this.line_generator = (day_scale, attribute_scale, attribute_name) => {
      return d3
        .line()
        .x(function(d) {
          return day_scale(d.day);
        })
        .y(function(d) {
          return attribute_scale(d[attribute_name]);
        });
    };
  }
  initialize = () => {
    let svg = this.svg;
    let day_scale = this.make_x_scale();
    let attribute_scale = this.make_y_scale();
    let xAxis = d3
      .axisBottom()
      .scale(day_scale)
      .ticks(2);
    let yAxis = d3
      .axisLeft()
      .scale(attribute_scale)
      .ticks(2);
    svg
      .append("text")
      .attr("x", this.x + this.width / 2)
      .attr("y", this.y + this.padding)
      .attr("fill", "black")
      .text(this.name);
    
    svg
      .append("g")
      .attr("class", "x_axis")
      .attr("id", "x_axis_" + this.id)
      .attr("transform", "translate(0," + (this.height + this.y) + ")")
      .call(xAxis);

    // Add the Y Axis
    svg
      .append("g")
      .attr("class", "y_axis")
      .attr("id", "y_axis_" + this.id)
      .attr("transform", "translate(" + this.padding + ",0)")
      .call(yAxis);

    svg
      .selectAll(".data_points_" + this.id)
      .data(this.data)
      .enter()
      .append("circle")
      .attrs({
        class: "data_points_" + this.id,
        cx: d => {
          return this.make_x_scale()(d.day);
        },
        cy: d => {
          return this.make_y_scale()(d[this.attribute]);
        },
        r: 2,
        fill: "#07103A"
      });

    svg
      .append("path")
      .data([this.data])
      .attr("id", "graph_path_" + this.id)
      .attr("class", "graph_path")
      .attr(
        "d",
        this.line_generator(
          this.make_x_scale(),
          this.make_y_scale(),
          this.attribute
        )
      );
  };

  addDayReport = report => {
    report["day"] = this.num_days;
    this.data.push(report);
    if (report[this.attribute] > this.max_val) {
      this.max_val = report[this.attribute];
    }
  };
  clear = () => {
    this.data = [];
    this.num_days = 0;
    this.svg.selectAll("#x_axis_" + this.id).remove();
    this.svg.selectAll("#y_axis_" + this.id).remove();
    this.svg.selectAll("#graph_path_" + this.id).remove();
    this.svg.selectAll(".data_points_" + this.id).remove();
    this.initialize();
  };
  update = report => {
    this.num_days++;
    this.addDayReport(report);

    let day_scale = this.make_x_scale();
    let attribute_scale = this.make_y_scale();

    let xAxis = d3
      .axisBottom()
      .scale(day_scale)
      .ticks(2);
    let yAxis = d3
      .axisLeft()
      .scale(attribute_scale)
      .ticks(2);
    this.svg.selectAll("#x_axis_" + this.id).remove();
    this.svg.selectAll("#y_axis_" + this.id).remove();

    this.svg
      .append("g")
      .attr("class", "x_axis")
      .attr("id", "x_axis_" + this.id)
      .attr("transform", "translate(0," + (this.y + this.height) + ")")
      .call(xAxis);

    // Add the Y Axis
    this.svg
      .append("g")
      .attr("class", "y_axis")
      .attr("id", "y_axis_" + this.id)
      .attr("transform", "translate(" + this.padding + ",0)")
      .call(yAxis);

    let point_selection = this.svg.selectAll(".data_points_" + this.id);
    point_selection
      .data(this.data)
      .transition()
      .duration(400)
      .attrs({
        class: "data_points_" + this.id,
        cx: d => {
          return day_scale(d.day);
        },
        cy: d => {
          return attribute_scale(d[this.attribute]);
        },
        r: 2,
        fill: "#07103A"
      });

    let path_selection = this.svg.selectAll("#graph_path_" + this.id);
    path_selection
      .data([this.data])
      .transition()
      .duration(400)
      .attrs({
        d: this.line_generator(day_scale, attribute_scale, this.attribute)
      });

    point_selection
      .data(this.data)
      .enter()
      .append("circle")
      .attrs({
        class: "data_points_" + this.id,
        cx: d => {
          return day_scale(d.day);
        },
        cy: d => {
          return attribute_scale(d[this.attribute]);
        },
        r: 2,
        fill: "#07103A"
      });
  };
}

class Viz {
  constructor(svg, x, y, w, h) {
    let ph = h - 2 * 45;
    //ph = h;
    this.num_metrics = 4;
    this.plots = {};
    this.plots["entries_graph"] = new TrackingGraph(
      svg,
      x,
      y,
      w,
      ph / this.num_metrics,
      "entries",
      0,
      (name = "customers")
    );
    this.plots["revenue_graph"] = new TrackingGraph(
      svg,
      x,
      y + ph / this.num_metrics,
      w,
      ph / this.num_metrics,
      "revenue",
      1
    );
    this.plots["profit_graph"] = new TrackingGraph(
      svg,
      x,
      y + (2 * ph) / this.num_metrics,
      w,
      ph / this.num_metrics,
      "profit",
      2
    );
    this.plots["satisfaction_graph"] = new TrackingGraph(
      svg,
      x,
      y + (3 * ph) / this.num_metrics,
      w,
      ph / this.num_metrics,
      "satisfaction",
      3,
      (name = "customer satisfaction")
    );
  }

  initialize() {
    for (let metric in this.plots) {
      this.plots[metric].initialize();
    }
  }
  update(report) {
    for (let metric in this.plots) {
      this.plots[metric].update(report);
    }
  }
  clear() {
    for (let metric in this.plots) {
      this.plots[metric].clear();
    }
  }
}

function generateRating(title, rating, icon) {
  console.log(title, rating);
  let stringBuilder = "<p>";
  stringBuilder += title + ": ";
  for (let i = 0; i < rating; i++) {
    stringBuilder += "<i class='material-icons'>" + icon + "</i>";
  }
  stringBuilder += "</p>";
  return stringBuilder;
}

function showReport(report) {
  $("#report").empty();
  $("#ratings").empty();
  $("#finances").empty();
  $("#report").append("<h2>Restaurant Simulation Summary</h2>");
  $("#ratings").append("<h3>Ratings and Reviews</h3>");
  $("#ratings").append(
    "<p>Number of Days Simulated: " + report["num_days"] + "</p>"
  );
  $("#ratings").append(
    generateRating(
      "Overall Rating",
      Math.round(report["satisfaction"] * 7),
      "star"
    )
  );
  $("#ratings").append(
    generateRating(
      "Price Range",
      Math.round(report["avg_normalized_check"] * 7),
      "attach_money"
    )
  );
  $("#ratings").append(
    generateRating(
      "Service Rating",
      Math.round(report["service_rating"] * 5),
      "sentiment_satisfied"
    )
  );
  $("#ratings").append(
    generateRating(
      "Busyness",
      Math.ceil(report["daily_customers"] / 50),
      "person"
    )
  );
  $("#ratings").append(
    generateRating("Noisiness", Math.round(report["avg_noise"] / 4), "hearing")
  );
  $("#ratings").append(
    "<p>Average Wait Time: " +
      report["wait_times"][0].toLocaleString(undefined, {
        maximumFractionDigits: 2
      }) +
      "</p>"
  );
  $("#ratings").append(
    "<p>Average Group Size: " +
      report["avg_party_size"].toLocaleString(undefined, {
        maximumFractionDigits: 2
      }) +
      "</p>"
  );
  $("#finances").append("<h3>Finances</h3>");
  $("#finances").append(
    "<p>Total Revenue: <span class='revenue'>$" +
      report["revenue"].toLocaleString(undefined, {
        maximumFractionDigits: 2
      }) +
      "</span></p>"
  );
  $("#finances").append(
    "<p>Upfront Costs: <span class='expenses'>$" +
      report["upfront_costs"].toLocaleString(undefined, {
        maximumFractionDigits: 2
      }) +
      "</span></p>"
  );
  $("#finances").append(
    "<p>Staffing, Food, and Upkeep Costs: <span class='expenses'>$" +
      report["total_overhead"].toLocaleString(undefined, {
        maximumFractionDigits: 2
      }) +
      "</span></p>"
  );
  let profitability = "expenses";
  if (report["profit"] > 0) {
    profitability = "revenue";
  }
  $("#finances").append(
    "<p>Profit: <span class='" +
      profitability +
      "'>$" +
      report["profit"].toLocaleString(undefined, { maximumFractionDigits: 2 }) +
      "</span></p>"
  );
}
