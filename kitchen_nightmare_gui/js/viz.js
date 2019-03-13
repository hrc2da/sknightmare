class NoiseGraph {
    constructor(svg, x, y, w, h) {
        this.svg = svg;
        this.num_days = 2;
        this.max_noise = 1.0;
        this.min_noise = 0.0;
        this.padding = 25;
        this.x = x;
        this.width = w;
        this.y = y;
        this.height = h;
        this.day_scale = d3.scaleLinear()
            .domain([0, this.num_days])
            .range([this.x + this.padding, this.x + this.width]);
        this.noise_scale = d3.scaleLinear()
            .domain([this.max_noise, this.min_noise])
            .range([this.y + this.padding, this.y + this.height]);
        this.data = [{
            'day': 1,
            'noise': 0.5
        }];
    }
    initialize = () => {
        let svg = this.svg;

        let xAxis = d3.axisBottom().scale(this.day_scale).ticks(this.num_days)
        let yAxis = d3.axisLeft().scale(this.noise_scale)

        svg.append("g")
            .attr("class", "x axis")
            .attr("id", "noise_x_axis")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xAxis);

        // Add the Y Axis
        svg.append("g")
            .attr("class", "y axis")
            .attr("id", " noise_y_axis")
            .attr("transform", "translate(" + this.padding + ",0)")
            .call(yAxis);

        svg.selectAll(".data_points")
            .data(this.data)
            .enter()
            .append('circle')
            .attrs({
                class: 'data_points',
                cx: (d) => {
                    return this.day_scale(d.day)
                },
                cy: (d) => {
                    return this.noise_scale(d.noise)
                },
                r: 2,
                fill: '#07103A'
            })
    }

    update = (report) => {
        console.log(report);
        this.num_days++
        this.data.push(report);
        this.day_scale = d3.scaleLinear()
            .domain([0, this.num_days])
            .range([this.x + this.padding, this.x + this.width]);

        let xAxis = d3.axisBottom().scale(this.day_scale).ticks(this.num_days);
        this.svg.selectAll("#noise_x_axis").remove();

        this.svg.append("g")
            .attr("class", "x axis")
            .attr("id", "noise_x_axis")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xAxis);

        let point_selection = this.svg.selectAll(".data_points");
        point_selection.data(this.data)
            .transition()
            .duration(400)
            .attrs({
                class: 'data_points',
                cx: (d) => {
                    return this.day_scale(d.day)
                },
                cy: (d) => {
                    return this.noise_scale(d.noise)
                },
                r: 2,
                fill: '#07103A'
            });


        point_selection.data(this.data).enter()
            .append('circle')
            .attrs({
                class: 'data_points',
                cx: (d) => {
                    return this.day_scale(d.day)
                },
                cy: (d) => {
                    return this.noise_scale(d.noise)
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