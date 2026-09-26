#include <TargetConditionals.h>
#if TARGET_OS_IPHONE

#include "Platform.h"
#include "../OpenRCT2.h"
#include "../core/Path.hpp"
#include "../localisation/Language.h"
#include <Foundation/Foundation.h>

namespace OpenRCT2::Platform
{
    static std::string Directory(NSSearchPathDirectory directory)
    {
        NSURL* url = [[NSFileManager defaultManager] URLsForDirectory:directory inDomains:NSUserDomainMask].firstObject;
        return url == nil ? std::string() : std::string(url.path.UTF8String);
    }

    std::string GetFolderPath(SpecialFolder folder)
    {
        switch (folder)
        {
            case SpecialFolder::userCache: return Directory(NSCachesDirectory);
            case SpecialFolder::userConfig:
            case SpecialFolder::userData:
            case SpecialFolder::userHome: return Directory(NSDocumentDirectory);
            default: return {};
        }
    }

    std::string GetDocsPath() { return [NSBundle mainBundle].resourcePath.UTF8String; }
    std::string GetInstallPath()
    {
        if (gCustomOpenRCT2DataPath[0] != '\0') return Path::GetAbsolute(gCustomOpenRCT2DataPath);
        return [NSBundle mainBundle].resourcePath.UTF8String;
    }
    std::string GetCurrentExecutablePath() { return [NSBundle mainBundle].executablePath.UTF8String; }
    u8string StrDecompToPrecomp(u8string_view input)
    {
        auto value = u8string(input);
        NSString* string = [NSString stringWithUTF8String:value.c_str()];
        return string == nil ? value : u8string(string.precomposedStringWithCanonicalMapping.UTF8String);
    }
    bool HandleSpecialCommandLineArgument(const char*) { return false; }
    uint16_t GetLocaleLanguage()
    {
        for (NSString* preferred in [NSLocale preferredLanguages])
        {
            auto language = LanguageGetIDFromLocale(preferred.UTF8String);
            if (language != LANGUAGE_UNDEFINED) return language;
        }
        return LANGUAGE_ENGLISH_UK;
    }
    CurrencyType GetLocaleCurrency()
    {
        NSString* code = [[NSLocale currentLocale] objectForKey:NSLocaleCurrencyCode];
        return GetCurrencyValue(code.UTF8String);
    }
    MeasurementFormat GetLocaleMeasurementFormat()
    {
        NSNumber* metric = [[NSLocale currentLocale] objectForKey:NSLocaleUsesMetricSystem];
        return metric.boolValue ? MeasurementFormat::metric : MeasurementFormat::imperial;
    }
    SteamPaths GetSteamPaths() { return {}; }
    std::vector<std::string> GetSearchablePathsRCT1() { return {}; }
    std::vector<std::string> GetSearchablePathsRCT2()
    {
        return { Path::Combine(GetFolderPath(SpecialFolder::userData), "RCT2") };
    }
}
#endif
