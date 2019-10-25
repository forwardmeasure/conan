#include <cassert>
#include <string>

#include <outcome.hpp>
namespace outcome = OUTCOME_V2_NAMESPACE;

outcome::result<std::string> get_value() {
    return "hello";
}

int main() {
    assert(get_value().assume_value() == "hello");
    return 0;
}
