class NoiseGraph {
    constructor(svg, x, y, w, h) {
        this.svg = svg;
        this.num_days = 2;
        this.max_noise = 10.0;
        this.min_noise = 0.0;
        this.padding = 25;
        this.x = x;
        this.width = w;
        this.y = y;
        this.height = h;
        this.make_x_scale = () => {
            return d3.scaleLinear()
                .domain([0, this.num_days])
                .range([this.x + this.padding, this.x + this.width]);
        }
        this.make_y_scale = () => {
            return d3.scaleLinear()
                .domain([this.max_noise, this.min_noise])
                .range([this.y + this.padding, this.y + this.height]);
        }
        this.data = [{
            "day": 1,
            "noise": 10
        }];

        this.line_generator = (day_scale, noise_scale) => {
            return d3.line()
                .x(function (d) {
                    return day_scale(d.day);
                })
                .y(function (d) {
                    return noise_scale(d.noise);
                })
        };
    }
    initialize = () => {
        let svg = this.svg;
        let day_scale = this.make_x_scale();
        let noise_scale = this.make_y_scale();
        let xAxis = d3.axisBottom().scale(day_scale).ticks(this.num_days)
        let yAxis = d3.axisLeft().scale(noise_scale).ticks(1)

        svg.append("g")
            .attr("class", "x axis")
            .attr("id", "noise_x_axis")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xAxis);

        // Add the Y Axis
        svg.append("g")
            .attr("class", "y axis")
            .attr("id", "noise_y_axis")
            .attr("transform", "translate(" + this.padding + ",0)")
            .call(yAxis);

        svg.selectAll(".data_points")
            .data(this.data)
            .enter()
            .append('circle')
            .attrs({
                class: 'data_points',
                cx: (d) => {
                    return this.make_x_scale()(d.day)
                },
                cy: (d) => {
                    return this.make_y_scale()(d.noise)
                },
                r: 2,
                fill: '#07103A'
            })

        svg.append("path")
            .data([this.data])
            .attr("class", "graph_path")
            .attr("d", this.line_generator(this.make_x_scale(), this.make_y_scale()));

    };

    addDayReport = (report) => {
        report['day'] = this.num_days;
        report['noise'] = report['entries'];
        this.data.push(report);
        if (report.entries > this.max_noise) {
            this.max_noise = report.entries;
        }
    }

    update = (report) => {
        this.num_days++;
        this.addDayReport(report)

        let day_scale = this.make_x_scale();
        let noise_scale = this.make_y_scale();

        let xAxis = d3.axisBottom().scale(day_scale).ticks(2);
        let yAxis = d3.axisLeft().scale(noise_scale).ticks(2)
        this.svg.selectAll("#noise_x_axis").remove();
        this.svg.selectAll("#noise_y_axis").remove();

        this.svg.append("g")
            .attr("class", "x axis")
            .attr("id", "noise_x_axis")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xAxis);

        // Add the Y Axis
        this.svg.append("g")
            .attr("class", "y axis")
            .attr("id", "noise_y_axis")
            .attr("transform", "translate(" + this.padding + ",0)")
            .call(yAxis);

        let point_selection = this.svg.selectAll(".data_points");
        point_selection.data(this.data)
            .transition()
            .duration(400)
            .attrs({
                class: 'data_points',
                cx: (d) => {
                    return day_scale(d.day)
                },
                cy: (d) => {
                    return noise_scale(d.noise)
                },
                r: 2,
                fill: '#07103A'
            });

        let path_selection = this.svg.selectAll(".graph_path");
        path_selection.data([this.data])
            .transition()
            .duration(400)
            .attrs({
                "d": this.line_generator(day_scale, noise_scale)
            });


        point_selection.data(this.data).enter()
            .append('circle')
            .attrs({
                class: 'data_points',
                cx: (d) => {
                    return day_scale(d.day)
                },
                cy: (d) => {
                    return noise_scale(d.noise)
                },
                r: 2,
                fill: '#07103A'
            })

    }

}

class Viz {
    constructor(svg, x, y, w, h) {
        this.num_metrics = 4;
        this.noise_graph = new NoiseGraph(svg, x, y, w, h / this.num_metrics);
    }

    initialize() {
        this.noise_graph.initialize();
    }
    update(report) {
        this.noise_graph.update(report);
    }
}