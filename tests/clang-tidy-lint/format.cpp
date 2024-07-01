// keep: all 'modernize', except 'modernize-use-nullptr' and 'modernize-use-nodiscard'
#include <iostream> // NOLINT(modernize-avoid-bind)

// NOLINTBEGIN(foo)
// NOLINTBEGIN(foo,modernize-avoid-bind)

// A nolint comment.
// modernize-avoid-bind
// NOLINT
// NOLINTNEXTLINE (modernize-use-nullptr)
// NOLINTBEGIN
//

int i = 0; // NOLINT( modernize-avoid-bind )
int j = 0; // NOLINT(modernize-*, readability-*)
int k = 0; // NOLINT(readability-*)
int x = 0; //  NOLINT(*-use-nodiscard)

// NOLINT(modernize-avoid-bind, modernize-use-using,modernize-avoid-c-arrays)
// NOLINT(bugprone-undefined-memory-manipulation,modernize-avoid-bind,modernize-avoid-c-arrays, modernize-use-using)
// NOLINT(modernize-use-nullptr)
// NOLINT(modernize-use-nullptr,modernize-avoid-bind) Some Comment
// NOLINT(modernize-use-nullptr, modernize-avoid-bind)
// NOLINT(modernize-avoid-bind,modernize-use-nullptr)
// NOLINT(modernize-use-nullptr,modernize-use-nullptr) Comment
int xyz = 0; // NOLINT(foo-bar, *-bar, foo-*)

// NOLINTNEXTLINE(modernize-use-using, foo)
int main() {
  std::cout << "Hello, World!" << std::endl; // NOLINT(modernize-use-nullptr,modernize-use-using, *keep-me,modernize-use-nullptr)
  std::cout << "NOLINT(modernize-use-nullptr)" << std::endl;   // NOLINT(modernize-use-nullptr)

  return 0; // NOLINT(test-keep-me,test-keep-me2,clang-diagnostic-error)
}
// NOLINTEND(modernize-avoid-bind)
// NOLINTEND(foo)

/// EOF
