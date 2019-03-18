class Staff {
    constructor(x, y) {
        this.type = 'circle';
        this.size = 15;
        this.x_original = x;
        this.y_original = y;
    }

    draw = () => {
        let svg_type = this.type;
        let attrs = {}
        attrs['svg_type'] = svg_type;
        attrs['data'] = [{
            'x': this.x_original,
            'y': this.y_original,
            'size': this.size,
            'text_pad': 6,
        }];
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
        attrs['text'] = "W";
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