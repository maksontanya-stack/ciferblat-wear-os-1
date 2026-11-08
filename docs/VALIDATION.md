# Проверки версии 1.0.0

- Официальный `wff-validator` 1.7.0: XML соответствует Watch Face Format v1.
- Gradle `assembleRelease` и `lintRelease`: успешно.
- `apksigner verify`: успешно, подпись APK Signature Scheme v3, совместимая с minSdk 33.
- Сертификат подписи SHA-256: `29caf7fbab6fe306746fcc30d94a9f42822312ada2a6ccdd43556eba7ba343f4`.
- Официальный Memory Footprint Evaluator: PASS; max active 4 102 328 байт, max ambient 3 930 240 байт.
- Проверка графики: тёмный мастер пиксельно равен исходному фрагменту; темы 450×450 RGBA.
- Проверка runtime: полный набор 24 часов / 60 минут для двух тем, уникальные ID трёх полей данных, отображение отсутствующих данных, отдельный AOD.

Smoke test эмулятора выполняется отдельно workflow `emulator.yml`; результат и снимки доступны в Actions. Физическая Galaxy Watch4 Classic из этой среды недоступна. Доступность пульса, погоды и этажей зависит от установленных на часах провайдеров; синхронизация с Samsung Health здесь не подтверждена.

Статические снимки `design/` не являются доказательством запуска на часах.

## Подтверждённый запуск

[Smoke test Wear OS 4 — успешно](https://github.com/maksontanya-stack/ciferblat-wear-os-1/actions/runs/42483751442): установка, выбор циферблата, рендеринг обоих полей времени и переход минут. Снимки: [первый кадр](screenshots/active-first.png), [следующая минута](screenshots/active-next-minute.png). На эмуляторе недоступен источник шагов — проверено отображение прочерка.

[Сборка релизного пакета — успешно](https://github.com/maksontanya-stack/ciferblat-wear-os-1/actions/runs/42484051893): официальный XML validator, проверка ресурсов, Android Lint, отсутствие DEX и официальный Memory Footprint Evaluator. После сборки APK подписан локально; подпись проверена `apksigner verify`.

Автоматический smoke test не заменяет проверку провайдеров Samsung на физической Watch4 Classic. Светлая настройка и AOD описаны и проверены структурно; отдельный интерактивный тест их переключения в эмуляторе не выполнялся.
