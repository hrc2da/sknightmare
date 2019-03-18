class TrackingGraph {
    constructor(svg, x, y, w, h, attribute) {
        this.svg = svg;
        this.attribute = attribute;
        this.num_days = 0;
        this.max_val = 10.0;
        this.min_val = 0.0;
        this.padding = 25;
        this.x = x;
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
                .x(function (d) {
                    return day_scale(d.day);
                })
                .y(function (d) {
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

        svg.append("g")
            .attr("class", "x_axis")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xAxis);

        // Add the Y Axis
        svg.append("g")
            .attr("class", "y_axis")
            .attr("transform", "translate(" + this.padding + ",0)")
            .call(yAxis);

        svg.selectAll(".data_points")
            .data(this.data)
            .enter()
            .append("circle")
            .attrs({
                class: "data_points",
                cx: d => {
                    return this.make_x_scale()(d.day);
                },
                cy: d => {
                    return this.make_y_scale()(d[this.attribute]);
                },
                r: 2,
                fill: "#07103A"
            });

        svg.append("path")
            .data([this.data])
            .attr("class", "graph_path")
            .attr("d", this.line_generator(this.make_x_scale(), this.make_y_scale(), this.attribute));
    };

    addDayReport = report => {
        report["day"] = this.num_days;
        this.data.push(report);
        if (report[this.attribute] > this.max_val) {
            this.max_val = report[this.attribute];
        }
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
        this.svg.selectAll(".x_axis").remove();
        this.svg.selectAll(".y_axis").remove();

        this.svg
            .append("g")
            .attr("class", "x_axis")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xAxis);

        // Add the Y Axis
        this.svg
            .append("g")
            .attr("class", "y_axis")
            .attr("transform", "translate(" + this.padding + ",0)")
            .call(yAxis);

        let point_selection = this.svg.selectAll(".data_points");
        point_selection
            .data(this.data)
            .transition()
            .duration(400)
            .attrs({
                class: "data_points",
                cx: d => {
                    return day_scale(d.day);
                },
                cy: d => {
                    return attribute_scale(d[this.attribute]);
                },
                r: 2,
                fill: "#07103A"
            });

        let path_selection = this.svg.selectAll(".graph_path");
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
                class: "data_points",
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
        this.num_metrics = 4;
        this.entries_graph = new TrackingGraph(svg, x, y, w, h / this.num_metrics, "entries");
    }

    initialize() {
        this.entries_graph.initialize();
    }
    update(report) {
        console.log(report);
        this.entries_graph.update(report);
    }
}