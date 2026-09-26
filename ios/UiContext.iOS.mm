#include <TargetConditionals.h>
#if TARGET_OS_IPHONE

#include "UiContext.h"
#include <SDL_messagebox.h>
#include <UIKit/UIKit.h>
#include <openrct2/ui/UiContext.h>

namespace OpenRCT2::Ui
{
    class IOSContext final : public IPlatformUiContext
    {
    public:
        void SetWindowIcon(SDL_Window*) override {}
        bool IsSteamOverlayAttached() override { return false; }
        bool HasMenuSupport() override { return false; }
        int32_t ShowMenuDialog(const std::vector<std::string>&, const std::string&, const std::string&) override
        {
            return -1;
        }
        void ShowMessageBox(SDL_Window* window, const std::string& message) override
        {
            SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_WARNING, "OpenRCT2", message.c_str(), window);
        }
        void OpenFolder(const std::string&) override {}
        void OpenURL(const std::string& url) override
        {
            NSString* value = [NSString stringWithUTF8String:url.c_str()];
            NSURL* target = [NSURL URLWithString:value];
            if (target != nil && ([target.scheme isEqualToString:@"https"] || [target.scheme isEqualToString:@"http"]))
            {
                dispatch_async(dispatch_get_main_queue(), ^{
                    [[UIApplication sharedApplication] openURL:target options:@{} completionHandler:nil];
                });
            }
        }
        std::string ShowFileDialog(SDL_Window*, const FileDialogDesc&) override { return {}; }
        std::string ShowDirectoryDialog(SDL_Window*, const std::string&) override { return {}; }
        bool HasFilePicker() const override { return false; }
    };

    std::unique_ptr<IPlatformUiContext> CreatePlatformUiContext()
    {
        return std::make_unique<IOSContext>();
    }
}
#endif
