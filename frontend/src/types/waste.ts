export interface ClassificationResult {
    label: string;
    confidence: number;
    dsl_code: string;
    parse_tree_data: any; // Format of ANTLR parse tree data returned by the backend
}