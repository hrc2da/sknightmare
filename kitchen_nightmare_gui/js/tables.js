class Table {
    constructor(type, name, seats, size, cost, upkeep, x, y, path) {
        this.type = type;
        this.name = name;
        this.seats = seats;
        this.size = size;
        this.cost = cost;
        this.daily_upkeep = upkeep;
        this.x_original = x;
        this.y_original = y;
        this.path = path;
        this.attributes = {
            "type": this.type,
            "seats": this.seats,
            "radius": this.size,
            "cost": this.cost,
            "daily_upkeep": this.daily_upkeep
        }
    }

    draw = () => {
        let svg_type = this.type;
        let attrs = {}
        attrs['svg_type'] = svg_type;
        attrs['data'] = [{
            'name': this.name,
            'x': this.x_original,
            'y': this.y_original,
            'size': this.size,
            'text_pad': 5,
            'attributes': this.attributes

        }];
        if (svg_type == 'image') {
            let shape_attrs = {
                x: function (d) {
                    return d.x - d.size;
                },
                y: function (d) {
                    return d.y - d.size;
                },
                "xlink:href": this.path,
                width: this.size * 2,
                height: this.size * 2,
            };
            attrs['shape_drag_attrs'] = {
                x: function (d) {
                    d.x = d3.mouse(this)[0] - d.size
                    return d.x;
                },

                y: function (d) {
                    d.y = d3.mouse(this)[1] - d.size
                    return d.y;
                },
            }
            attrs['shape_attrs'] = shape_attrs;
        } else if (svg_type == 'circle') {
            let shape_attrs = {
                cx: function (d) {
                    return d.x
                },
                cy: function (d) {
                    return d.y
                },
                r: this.size
            };
            attrs['shape_drag_attrs'] = {
                cx: function (d) {
                    d.x = d3.mouse(this)[0]
                    return d.x
                },
                cy: function (d) {
                    d.y = d3.mouse(this)[1]
                    return d.y
                },
            }
            attrs['shape_attrs'] = shape_attrs;
        }
        attrs['text'] = this.seats;
        attrs['text_attrs'] = {
            x: function (d) {
                return d.x - d.text_pad;
            },

            y: function (d) {
                return d.y + d.text_pad;
            },
            fill: 'white'
        }
        attrs['text_drag_attrs'] = {
            x: function (d) {
                d.x = d3.mouse(this)[0] - d.text_pad;
                return d.x;
            },

            y: function (d) {
                d.y = d3.mouse(this)[1] + d.text_pad;
                return d.y;
            },
        }
        return attrs;
    }
}