# rails/rails
Source: https://github.com/rails/rails/releases

## v8.1.2 | 2026-01-08T20:17:17Z | draft
Link: https://github.com/rails/rails/releases/tag/v8.1.2

## Active Support

-
Make delegate and delegate_missing_to work in BasicObject subclasses.

Rafael Mendonça França

-
Fix Inflectors when using a locale that fallbacks to :en.

Said Kaldybaev

-
Fix ActiveSupport::TimeWithZone#as_json to consistently return UTF-8 strings.

Previously the returned string would sometime be encoded in US-ASCII, which in

some cases may be problematic.

Now the method consistently always return UTF-8 strings.

Jean Boussier

-
Fix TimeWithZone#xmlschema when wrapping a DateTime instance in local time.

Previously it would return an invalid time.

Dmytro Rymar

-
Implement LocalCache strategy on ActiveSupport::Cache::MemoryStore. The memory store

needs to respond to the same interface as other cache stores (e.g. ActiveSupport::NullStore).

Mikey Gough

-
Fix ActiveSupport::Inflector.humanize with international characters.

ActiveSupport::Inflector.humanize("áÉÍÓÚ")  # => "Áéíóú"
ActiveSupport::Inflector.humanize("аБВГДЕ") # => "Абвгде"
## v8.1.0.beta1 | 2025-09-04T12:30:05Z | prerelease
Link: https://github.com/rails/rails/releases/tag/v8.1.0.beta1

## Active Support

-
Add ActiveSupport::Cache::Store#namespace= and #namespace.

Can be used as an alternative to Store#clear in some situations such as parallel

testing.

Nick Schwaderer

-
Create parallel_worker_id helper for running parallel tests. This allows users to

know which worker they are currently running in.

Nick Schwaderer

-
Make the cache of ActiveSupport::Cache::Strategy::LocalCache::Middleware updatable.

If the cache client at Rails.cache of a booted application changes, the corresponding

mounted middleware needs to update in order for request-local caches to be setup properly.

Otherwise, redundant cache operations will erroneously hit the datastore.

Gannon McGibbon

-
Add assert_events_reported test helper for ActiveSupport::EventReporter.

This new assertion allows testing multiple events in a single block, regardless of order:

assert_events_reported([
  { name: "user.created", payload: { id: 123 } },
  { name: "email.sent", payload: { to: "user@example.com" } }
]) do
  create_user_and_send_welcome_email
end
## v8.0.0 | 2024-11-07T22:29:02Z | prerelease
Link: https://github.com/rails/rails/releases/tag/v8.0.0

## Active Support

-
Remove deprecated support to passing an array of strings to ActiveSupport::Deprecation#warn.

Rafael Mendonça França

-
Remove deprecated support to setting attr_internal_naming_format with a @ prefix.

Rafael Mendonça França

-
Remove deprecated ActiveSupport::ProxyObject.

Rafael Mendonça França

-
Don't execute i18n watcher on boot. It shouldn't catch any file changes initially,

and unnecessarily slows down boot of applications with lots of translations.

Gannon McGibbon, David Stosik

-
Fix ActiveSupport::HashWithIndifferentAccess#stringify_keys to stringify all keys not just symbols.

Previously:

{ 1 => 2 }.with_indifferent_access.stringify_keys[1] # => 2
## v7.1.4.1 | 2024-10-15T20:39:03Z | prerelease
Link: https://github.com/rails/rails/releases/tag/v7.1.4.1

## Active Support

- No changes.

## Active Model

- No changes.

## Active Record

- No changes.

## Action View

- No changes.

## Action Pack

-
Avoid regex backtracking in HTTP Token authentication

[CVE-2024-47887]

-
Avoid regex backtracking in query parameter filtering

[CVE-2024-41128]

## Active Job

- No changes.

## Action Mailer

-
Avoid regex backtracking in block_format helper

[CVE-2024-47889]

## Action Cable

- No changes.

## Active Storage

- No changes.

## Action Mailbox

- No changes.

## Action Text

-
Avoid backtracing in plain_text_for_blockquote_node

[CVE-2024-47888]

## Railties

- No changes.

## Guides

- No changes.
## v7.1.3.4 | 2024-06-04T18:07:09Z | prerelease
Link: https://github.com/rails/rails/releases/tag/v7.1.3.4

## Active Support

- No changes.

## Active Model

- No changes.

## Active Record

- No changes.

## Action View

- No changes.

## Action Pack

- Include the HTTP Permissions-Policy on non-HTML Content-Types

[CVE-2024-28103]

## Active Job

- No changes.

## Action Mailer

- No changes.

## Action Cable

- No changes.

## Active Storage

- No changes.

## Action Mailbox

- No changes.

## Action Text

- Sanitize ActionText HTML ContentAttachment in Trix edit view

[CVE-2024-32464]

## Railties

- No changes.
## v7.1.3 | 2024-01-16T23:02:49Z | prerelease
Link: https://github.com/rails/rails/releases/tag/v7.1.3

## Active Support

-
Handle nil backtrace_locations in ActiveSupport::SyntaxErrorProxy.

Eugene Kenny

-
Fix ActiveSupport::JSON.encode to prevent duplicate keys.

If the same key exist in both String and Symbol form it could

lead to the same key being emitted twice.

Manish Sharma

-
Fix ActiveSupport::Cache::Store#read_multi when using a cache namespace

and local cache strategy.

Mark Oleson

-
Fix Time.now/DateTime.now/Date.today to return results in a system timezone after #travel_to.

There is a bug in the current implementation of #travel_to:

it remembers a timezone of its argument, and all stubbed methods start

returning results in that remembered timezone. However, the expected

behaviour is to return results in a system timezone.

Aleksei Chernenkov

-
Fix :unless_exist option for MemoryStore#write (et al) when using a

cache namespace.

S. Brent Faulkner

-
Fix ActiveSupport::Deprecation to handle blaming generated code.

Jean Boussier, fatkodima

## Active Model

- No changes.

## Active Record

-
Fix Migrations with versions older than 7.1 validating options given to

add_reference.

Hartley McGuire

-
Ensure reload sets correct owner for each association.

Dmytro Savochkin

-
Fix view runtime for controllers with async queries.

fatkodima

-
Fix load_async to work with query cache.

fatkodima

-
Fix polymorphic belongs_to to correctly use parent's query_constraints.

fatkodima

-
Fix Preloader to not generate a query for already loaded association with query_constraints.

fatkodima

-
Fix multi-database polymorphic preloading with equivalent table names.

When preloading polymorphic associations, if two models pointed to two

tables with the same name but located in different databases, the

preloader would only load one.

Ari Summer

-
Fix encrypted_attribute? to take into account context properties passed to encrypts.

Maxime Réty

-
Fix find_by to work correctly in presence of composite primary keys.

fatkodima

-
Fix async queries sometimes returning a raw result if they hit the query cache.

ShipPart.async_count could return a raw integer rather than a Promise

if it found the result in the query cache.

fatkodima

-
Fix Relation#transaction to not apply a default scope.

The method was incorrectly setting a default scope around its block:

Post.where(published: true).transaction do
  Post.count # SELECT COUNT(*) FROM posts WHERE published = FALSE;
end
## v6.1.7.6 | 2023-08-22T20:23:23Z | release
Link: https://github.com/rails/rails/releases/tag/v6.1.7.6

No changes between this and 6.1.7.5.  This release was just to fix file permissions in the previous release.
## v6.1.7.2 | 2023-01-25T03:25:32Z | release
Link: https://github.com/rails/rails/releases/tag/v6.1.7.2

## Active Support

- No changes.

## Active Model

- No changes.

## Active Record

- No changes.

## Action View

- No changes.

## Action Pack

-
Fix domain: :all for two letter TLD

This fixes a compatibility issue introduced in our previous security

release when using domain: :all with a two letter but single level top

level domain domain (like .ca, rather than .co.uk).

## Active Job

- No changes.

## Action Mailer

- No changes.

## Action Cable

- No changes.

## Active Storage

- No changes.

## Action Mailbox

- No changes.

## Action Text

- No changes.

## Railties

- No changes.
## v5.2.8.1 | 2022-11-23T19:06:24Z | release
Link: https://github.com/rails/rails/releases/tag/v5.2.8.1

## Active Support

- No changes.

## Active Model

- No changes.

## Active Record

-
Change ActiveRecord::Coders::YAMLColumn default to safe_load

This adds two new configuration options The configuration options are as

follows:

- config.active_storage.use_yaml_unsafe_load

When set to true, this configuration option tells Rails to use the old

"unsafe" YAML loading strategy, maintaining the existing behavior but leaving

the possible escalation vulnerability in place.  Setting this option to true

is not recommended, but can aid in upgrading.

- config.active_record.yaml_column_permitted_classes

The "safe YAML" loading method does not allow all classes to be deserialized

by default.  This option allows you to specify classes deemed "safe" in your

application.  For example, if your application uses Symbol and Time in

serialized data, you can add Symbol and Time to the allowed list as follows:

config.active_record.yaml_column_permitted_classes = [Symbol, Date, Time]
## v5.2.7 | 2022-03-11T00:02:36Z | release
Link: https://github.com/rails/rails/releases/tag/v5.2.7

## Active Support

-
Restore support to Ruby 2.2.

ojab

## Active Model

- No changes.

## Active Record

- No changes.

## Action View

- No changes.

## Action Pack

- No changes.

## Active Job

- No changes.

## Action Mailer

- No changes.

## Action Cable

- No changes.

## Active Storage

-
Fix ActiveStorage.supported_image_processing_methods and

ActiveStorage.unsupported_image_processing_arguments that were not being applied.

Rafael Mendonça França

## Railties

- No changes.
