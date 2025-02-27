module.exports = grammar({
    name: 'math',

    precedences: _ => [
        [
            "exp",
            "mul",
            "add",
            "eq",
        ],
    ],

    rules: {
        expression: $ => choice(
            $._paren_expression,
            $._expression,
        ),
        _expression: $ => choice(
            $._var,
            $.num,
            $.add,
            $.sub,
            $.mul,
            $.div,
            $.int_div,
            $.exp,
            $.eq,
        ),

        add: $ => prec.left(
            "add",
            seq(field("left", $.expression), "+", field("right", $.expression)),
        ),

        sub: $ => prec.left(
            "add",
            seq(field("left", $.expression), "-", field("right", $.expression)),
        ),

        mul: $ => prec.left(
            "mul",
            seq(field("left", $.expression), optional(choice("*", "×", "·", "\\times", "\\cdot")), field("right", $.expression)),
        ),

        div: $ => prec.left(
            "mul",
            choice(
                seq(field("left", $.expression), choice("/", "\\div"), field("right", $.expression)),
                seq("\\frac{", field("left", $.expression), "}{", field("right", $.expression), "}"),
            )
        ),

        int_div: $ => prec.left(
            "mul",
            seq(field("left", $.expression), "//", field("right", $.expression)),)
        ,

        exp: $ => prec.left(
            "exp",
            seq(field("base", $.expression), choice("**", "^"), field("exp", $.expression)),
        ),

        eq: $ => prec.left(
            "eq",
            seq(field("left", $.expression), "=", field("right", $.expression)),
        ),

        _paren_expression: $ => prec(1, choice(
            seq("$", choice($._expression, $._paren_expression), "$"),
            seq("(", choice($._expression, $._paren_expression), ")"),
            seq("[", choice($._expression, $._paren_expression), "]"),
            seq("{", choice($._expression, $._paren_expression), "}"),
            seq("\\(", choice($._expression, $._paren_expression), "\\)"),
            seq("\\[", choice($._expression, $._paren_expression), "\\]"),
            seq("\\boxed{", choice($._expression, $._paren_expression), "}"),
            seq("\\left(", choice($._expression, $._paren_expression), "\\right)"),
        )),

        num: _ => /\d+(\.\d+)?/,

        var: _ => /([a-zA-Z][0-9a-zA-Z_]*)/,
        _m_var: $ => seq("\\text{", $._var, "}"),

        _var: $ => choice($.var, $._m_var),
    }
});
