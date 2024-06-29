// keep: all 'modernize', except 'modernize-use-nullptr' and 'modernize-use-nodiscard'
#include <iostream> // NOLINT(modernize-avoid-bind)


// NOLINTBEGIN(modernize-avoid-bind)

// A nolint comment.
// modernize-avoid-bind
// NOLINT
// NOLINTNEXTLINE (modernize-use-nullptr)
// NOLINTBEGIN
//

int i = 0; // NOLINT(modernize-avoid-bind)
int j = 0; // NOLINT(modernize-*)
int k = 0;
int x = 0;

// NOLINT(modernize-avoid-bind, modernize-use-using, modernize-avoid-c-arrays)
// NOLINT(modernize-avoid-bind, modernize-avoid-c-arrays, modernize-use-using)

// NOLINT(modernize-avoid-bind) Some Comment
// NOLINT(modernize-avoid-bind)
// NOLINT(modernize-avoid-bind)

int xyz = 0;

// NOLINTNEXTLINE(modernize-use-using)
int main() {
    std::cout << "Hello, World!" << std::endl; // NOLINT(modernize-use-using)
    std::cout << "NOLINT(modernize-use-nullptr)" << std::endl;
}
// NOLINTEND(modernize-avoid-bind)


/// EOF
