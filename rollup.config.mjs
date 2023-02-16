import {nodeResolve} from "@rollup/plugin-node-resolve"
export default {
  input: "./notes/assets/editor.mjs",
  output: {
    file: "./notes/static/javascript/note-taking/editor.bundle.js",
    format: "iife",
    name: 'cm6',
    exports: 'named'
  },
  plugins: [nodeResolve()]
}