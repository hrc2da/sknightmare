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
            },
            {
                'day': 2,
                'noise': 0.2
            }
        ];
    }
    load_graph = () => {
        let svg = this.svg;

        let xAxis = d3.axisBottom().scale(this.day_scale).ticks(this.num_days)
        let yAxis = d3.axisLeft().scale(this.noise_scale)

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xAxis);

        // Add the Y Axis
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + this.padding + ",0)")
            .call(yAxis);

        svg.selectAll(".data_points")
            .data(this.data)
            .enter()
            .append('circle')
            .attrs({
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