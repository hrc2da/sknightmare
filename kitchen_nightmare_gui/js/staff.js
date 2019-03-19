class Staff {
    constructor(x, y) {
        this.type = 'image';
        this.size = 25;
        this.x_original = x;
        this.y_original = y;
        this.path = 'svgs/waiter.svg'
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
            x: function (d) {
                return d.x
            },
            y: function (d) {
                return d.y
            },
            height: this.size,
            width: this.size,
            "xlink:href": this.path
        };
        attrs['shape_drag_attrs'] = {
            x: function (d) {
                d.x = d3.mouse(this)[0]
                return d.x
            },
            y: function (d) {
                d.y = d3.mouse(this)[1]
                return d.y
            },
        }
        attrs['shape_attrs'] = shape_attrs;
        return attrs;
    }
}