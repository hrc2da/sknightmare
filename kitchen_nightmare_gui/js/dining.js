class DiningRoom {
    constructor(w, h) {
        this.tables = [];
        this.num_tables = 0;
        this.items = [];
        this.num_items = 0;
        this.dining_bound_box = d3.select("#dining_layout");
        this.width = w;
        this.height = h;
    }

    // adds a table to the center of the dining table such that the user can drag it around the dining room 
    add_table = (table) => {
        // all the disparate places where there is table information
        let table_obj = table['table'];
        let table_svg_attrs = table['table_svg_attrs'];
        let table_svg = table['table_g'];

        // add drag handling to the table object
        let drag = d3.drag().on('drag', function (d) {
            d3.select(this).select(table_svg_attrs['svg_type']).attrs(table_svg_attrs['shape_drag_attrs']);
            d3.select(this).select('text').attrs(table_svg_attrs['text_drag_attrs']);
        })

        table_svg.call(drag);

        //update table tracking 
        this.num_tables++;
        this.tables.push(table);
    }

    add_item = (item) => {
        // all the disparate places where there is table information
        let item_obj = item['item'];
        let item_svg_attrs = item['item_svg_attrs'];
        let item_svg = item['item_g'];

        // add drag handling to the table object
        let drag = d3.drag().on('drag', function (d) {
            d3.select(this).select(item_svg_attrs['svg_type']).attrs(item_svg_attrs['shape_drag_attrs']);
            d3.select(this).select('text').attrs(item_svg_attrs['text_drag_attrs']);
        })

        item_svg.call(drag);

        //update table tracking 
        this.num_items++;
        this.items.push(item);
    }

    // export the current layout as a list of json objects
    get_layout = () => {
        let table_layout = []
        for (let table of this.tables) {
            let table_repr = {}
            table_repr['x'] = table['table_svg_attrs']['data'][0]['x'];
            table_repr['y'] = table['table_svg_attrs']['data'][0]['y'];
            table_repr['size'] = table['table'].size;
            table_repr['seats'] = table['table'].seats;
            table_repr['type'] = table['table'].type;
            table_repr['cost'] = table['table'].cost;
            table_repr['daily_upkeep'] = table['table'].daily_upkeep;
            table_repr['name'] = table['table'].name;
            table_repr['attributes'] = table['table'].attributes;
            table_repr['attributes']['x'] = table_repr['x']
            table_repr['attributes']['y'] = table_repr['y']
            table_layout.push(table_repr);
        }
        let equipment_layout = [];
        for (let eq of this.items) {
            let eq_repr = {};
            eq_repr['name'] = eq['item'].name;
            eq_repr['attributes'] = eq['item'].attributes;
            eq_repr['attributes']['x'] = eq['item_svg_attrs']['data'][0]['x'];
            eq_repr['attributes']['y'] = eq['item_svg_attrs']['data'][0]['y'];
            equipment_layout.push(eq_repr)
        }
        return {"tables":table_layout,"equipment":equipment_layout};
    }
}