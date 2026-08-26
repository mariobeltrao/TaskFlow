import {describe,expect,it,vi} from 'vitest';import {deadlineLabel} from './dates';
describe('deadlineLabel',()=>{it('marks completed tasks',()=>expect(deadlineLabel('2026-01-01',true)).toBe('Concluída'));it('calculates future deadlines',()=>{vi.useFakeTimers();vi.setSystemTime(new Date('2026-08-26T12:00:00'));expect(deadlineLabel('2026-08-28')).toBe('Faltam 2 dias');vi.useRealTimers()})});
