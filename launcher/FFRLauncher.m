// Native macOS bundle launcher. --inspect prints its plan without starting the host
// or creating user data. Compile with clang -fobjc-arc -framework Cocoa.
#import <Cocoa/Cocoa.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int fail(NSString *message) {
    fprintf(stderr, "FFR launcher: %s\n", message.UTF8String);
    [NSApplication sharedApplication];
    NSAlert *alert = [NSAlert new];
    alert.messageText = @"Unable to start FINAL FANTASY RESONANCE";
    alert.informativeText = message;
    [alert runModal];
    return 1;
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        BOOL inspect = argc == 2 && !strcmp(argv[1], "--inspect");
        NSBundle *bundle = NSBundle.mainBundle;
        NSString *resources = bundle.resourcePath;
        NSString *host = [bundle.bundlePath stringByAppendingPathComponent:@"Contents/MacOS/nativehost"];
        NSString *rewritten = [resources stringByAppendingPathComponent:@"rewritten"];
        NSString *state = [NSHomeDirectory() stringByAppendingPathComponent:@"Library/Application Support/FFRNative/0100B8A026F14000"];
        NSString *save = [state stringByAppendingPathComponent:@"save"];
        NSString *temp = [state stringByAppendingPathComponent:@"temp"];
        NSMutableDictionary<NSString *, NSString *> *env = [@{
            @"DM_ROOT": state,
            @"DM_ROMFS": [resources stringByAppendingPathComponent:@"romfs"],
            @"DM_SAVE": save, @"DM_TEMP": temp,
            @"DM_MSL_DIR": [resources stringByAppendingPathComponent:@"msl-cache"],
            @"DM_NVN_SHMAP": [resources stringByAppendingPathComponent:@"profile/shader_map.tsv"],
            @"DM_FONT_DIR": [resources stringByAppendingPathComponent:@"font"],
            @"DM_SHARED_FONT": @"/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            @"DM_PSO_USER": [state stringByAppendingPathComponent:@"pso_user.tsv"],
            @"DM_WINDOW": @"1", @"DM_AUDIO": @"1", @"DM_LANG": @"zh-Hans"
        } mutableCopy];
        NSString *aoc = [resources stringByAppendingPathComponent:@"aoc"];
        BOOL aocIsDirectory = NO;
        if ([NSFileManager.defaultManager fileExistsAtPath:aoc isDirectory:&aocIsDirectory] && aocIsDirectory)
            env[@"DM_AOC_DIR"] = aoc;
        NSData *fpsData = [NSData dataWithContentsOfFile:[resources stringByAppendingPathComponent:@"frame-rate-options.json"]];
        NSDictionary *fpsOptions = fpsData ? [NSJSONSerialization JSONObjectWithData:fpsData options:0 error:NULL] : nil;
        if ([fpsOptions isKindOfClass:NSDictionary.class] && [fpsOptions[@"game_menu"] boolValue])
            env[@"DM_FPS_FOLLOW_GAME"] = @"1";
        NSArray<NSString *> *args = @[host, rewritten, @"main", @"subsdk0", @"sdk"];
        if (inspect) {
            NSDictionary *plan = @{@"bundle": bundle.bundlePath, @"host_arguments": args,
                @"environment": env, @"working_directory": state,
                @"user_directories_created": @NO, @"host_started": @NO};
            NSData *json = [NSJSONSerialization dataWithJSONObject:plan options:NSJSONWritingPrettyPrinted | NSJSONWritingSortedKeys error:NULL];
            fwrite(json.bytes, 1, json.length, stdout); fputc('\n', stdout);
            return 0;
        }
        NSFileManager *fm = NSFileManager.defaultManager;
        if (![fm isExecutableFileAtPath:host]) return fail(@"The bundled nativehost executable is missing or not executable.");
        for (NSString *path in @[[resources stringByAppendingPathComponent:@"romfs/FFRS/Content/Paks/FFRS-Switch.ucas"],
                                  env[@"DM_NVN_SHMAP"], [resources stringByAppendingPathComponent:@"font/nintendo_ext.ttf"]]) {
            if (![fm isReadableFileAtPath:path]) return fail([@"A required bundled resource is missing: " stringByAppendingString:path]);
        }
        for (NSString *module in @[@"main", @"subsdk0", @"sdk"])
            for (NSString *suffix in @[@"patched.bin", @"fixups.tsv", @"gates.tsv"]) {
                NSString *path = [rewritten stringByAppendingPathComponent:[NSString stringWithFormat:@"%@.%@", module, suffix]];
                if (![fm isReadableFileAtPath:path]) return fail([@"A rewritten module file is missing: " stringByAppendingString:path]);
            }
        if (![fm isReadableFileAtPath:env[@"DM_SHARED_FONT"]]) return fail(@"This Mac does not have Arial Unicode.ttf at the expected system font path.");
        // Only a normal user launch reaches this point; inspect/build never creates saves.
        for (NSString *dir in @[state, save, temp]) {
            NSError *error = nil;
            if (![fm createDirectoryAtPath:dir withIntermediateDirectories:YES attributes:@{NSFilePosixPermissions: @0700} error:&error])
                return fail([NSString stringWithFormat:@"Cannot create user data directory %@: %@", dir, error.localizedDescription]);
        }
        NSString *log = [state stringByAppendingPathComponent:@"native.log"];
        int fd = open(log.fileSystemRepresentation, O_WRONLY | O_CREAT | O_APPEND, 0600);
        if (fd < 0) return fail([NSString stringWithFormat:@"Cannot open user log: %s", strerror(errno)]);
        if (dup2(fd, STDOUT_FILENO) < 0 || dup2(fd, STDERR_FILENO) < 0) { close(fd); return fail(@"Cannot redirect the host log."); }
        if (fd > STDERR_FILENO) close(fd);
        fprintf(stderr, "\nFFR native launch: %s\n", NSDate.date.description.UTF8String);
        // Drop inherited diagnostic/game paths so Finder and Terminal launches agree.
        for (NSString *key in NSProcessInfo.processInfo.environment)
            if ([key hasPrefix:@"DM_"]) unsetenv(key.UTF8String);
        for (NSString *key in env)
            if (setenv(key.UTF8String, env[key].fileSystemRepresentation, 1)) return fail(@"Cannot set the host environment.");
        if (chdir(state.fileSystemRepresentation)) return fail(@"Cannot select the user data directory.");
        char *hostArgs[6] = {0};
        for (NSUInteger i = 0; i < args.count; ++i) hostArgs[i] = strdup(args[i].fileSystemRepresentation);
        execv(host.fileSystemRepresentation, hostArgs);
        return fail([NSString stringWithFormat:@"nativehost could not start: %s", strerror(errno)]);
    }
}
