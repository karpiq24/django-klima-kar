const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const CompressionPlugin = require("compression-webpack-plugin");


module.exports = {
    optimization: {
        minimizer: [
            new UglifyJsPlugin({
                cache: true,
                parallel: true,
                sourceMap: true,
                extractComments: "all",
                uglifyOptions: {
                    compress: true,
                    output: null,
                },
            }),
            new OptimizeCSSAssetsPlugin({})
        ],
    },
    plugins: [
        new CompressionPlugin({
            test: /\.(js|css)/
        }),
        new UglifyJsPlugin(),
    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                },
            },
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
        ],
    },
};
