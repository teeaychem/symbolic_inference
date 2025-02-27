import XCTest
import SwiftTreeSitter
import TreeSitterMath

final class TreeSitterMathTests: XCTestCase {
    func testCanLoadGrammar() throws {
        let parser = Parser()
        let language = Language(language: tree_sitter_math())
        XCTAssertNoThrow(try parser.setLanguage(language),
                         "Error loading Math grammar")
    }
}
