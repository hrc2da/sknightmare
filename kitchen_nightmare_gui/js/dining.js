class DiningRoom {
    constructor(w, h) {
        this.tables = [];
        this.num_tables = 0;
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
            table_layout.push(table_repr);
        }
        return table_layout;
    }
}